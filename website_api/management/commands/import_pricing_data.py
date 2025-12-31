"""
Management-команда для импорта данных ценообразования.

Использование:
    python manage.py import_pricing_data
    python manage.py import_pricing_data --zones-only
    python manage.py import_pricing_data --dry-run
"""

from django.core.management.base import BaseCommand
from decimal import Decimal
from website_api.models import (
    City, Option, ParameterType, ParameterValue,
    OptionParameterType, ParameterPrice, DeliveryZone
)


class Command(BaseCommand):
    help = 'Импорт данных ценообразования из дампа мобильного приложения'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Только показать, что будет импортировано, без записи в БД',
        )
        parser.add_argument(
            '--zones-only',
            action='store_true',
            help='Импортировать только зоны доставки',
        )
        parser.add_argument(
            '--params-only',
            action='store_true',
            help='Импортировать только связи опций с параметрами',
        )

    def handle(self, *args, **options):
        self.dry_run = options['dry_run']
        
        if self.dry_run:
            self.stdout.write(self.style.WARNING('=== DRY RUN MODE ==='))
        
        self.stdout.write('Начало импорта данных ценообразования...\n')
        
        if options['zones_only']:
            self.import_delivery_zones()
        elif options['params_only']:
            self.link_options_to_parameters()
        else:
            # Полный импорт
            self.import_delivery_zones()
            self.link_options_to_parameters()
            self.import_parameter_prices()
        
        self.stdout.write(self.style.SUCCESS('\nИмпорт завершён!'))

    def import_delivery_zones(self):
        """Импорт зон доставки для всех городов"""
        self.stdout.write('1. Импорт зон доставки...')
        
        cities = City.objects.filter(is_active=True)
        created_count = 0
        updated_count = 0
        
        # Цены выезда по умолчанию для разных городов
        city_prices = {
            1: {'in_city': 0, 'out_city': 1500},      # Махачкала
            34: {'in_city': 0, 'out_city': 2500},     # Москва
            79: {'in_city': 0, 'out_city': 2000},     # Санкт-Петербург
            35: {'in_city': 0, 'out_city': 1500},     # Казань
            46: {'in_city': 0, 'out_city': 1500},     # Краснодар
        }
        
        # Дефолтные цены для остальных городов
        default_prices = {'in_city': 0, 'out_city': 1500}
        
        for city in cities:
            prices = city_prices.get(city.id, default_prices)
            
            for location_status, delivery_price in prices.items():
                zone_name = 'В городе' if location_status == 'in_city' else 'За городом'
                
                if self.dry_run:
                    self.stdout.write(
                        f'  [DRY] {city.title}: {zone_name} = {delivery_price} ₽'
                    )
                    continue
                
                zone, created = DeliveryZone.objects.update_or_create(
                    city=city,
                    location_status=location_status,
                    defaults={
                        'zone_name': zone_name,
                        'delivery_price': Decimal(str(delivery_price)),
                        'is_active': True,
                    }
                )
                
                if created:
                    created_count += 1
                else:
                    updated_count += 1
        
        if not self.dry_run:
            self.stdout.write(
                f'   Создано: {created_count}, обновлено: {updated_count}'
            )
            self.stdout.write(
                f'   Всего зон доставки: {DeliveryZone.objects.count()}'
            )

    def link_options_to_parameters(self):
        """Связывание опций с типами параметров"""
        self.stdout.write('\n2. Связывание опций с параметрами...')
        
        # Получаем типы параметров
        try:
            tire_radius = ParameterType.objects.get(code='tire_radius')
            fuel_type = ParameterType.objects.get(code='fuel_type')
            fuel_volume = ParameterType.objects.get(code='fuel_volume')
            lift_height = ParameterType.objects.get(code='lift_height')
        except ParameterType.DoesNotExist as e:
            self.stdout.write(self.style.ERROR(
                f'   Ошибка: тип параметра не найден. '
                f'Сначала загрузите fixtures: python manage.py loaddata parameter_types'
            ))
            return
        
        # Маппинг: ключевые слова в названии услуги/опции -> тип параметра
        param_mappings = [
            {
                'keywords': ['шиномонтаж', 'колес', 'шин'],
                'parameter_type': tire_radius,
                'is_required': True,
            },
            {
                'keywords': ['топлив', 'бензин', 'заправк'],
                'parameter_type': fuel_type,
                'is_required': True,
            },
            {
                'keywords': ['автовышка', 'вышка', 'подъём'],
                'parameter_type': lift_height,
                'is_required': True,
            },
        ]
        
        created_count = 0
        options_updated = 0
        
        for mapping in param_mappings:
            for keyword in mapping['keywords']:
                # Ищем опции по ключевым словам в названии услуги или опции
                options = Option.objects.filter(
                    is_active=True
                ).filter(
                    service__title__icontains=keyword
                ) | Option.objects.filter(
                    is_active=True
                ).filter(
                    title__icontains=keyword
                )
                
                for option in options.distinct():
                    if self.dry_run:
                        self.stdout.write(
                            f'  [DRY] {option.title} -> {mapping["parameter_type"].title}'
                        )
                        continue
                    
                    link, created = OptionParameterType.objects.update_or_create(
                        option=option,
                        parameter_type=mapping['parameter_type'],
                        defaults={'is_required': mapping['is_required']}
                    )
                    
                    if created:
                        created_count += 1
                    
                    if not option.has_parameters:
                        option.has_parameters = True
                        option.save()
                        options_updated += 1
        
        if not self.dry_run:
            self.stdout.write(
                f'   Создано связей: {created_count}'
            )
            self.stdout.write(
                f'   Опций с параметрами: {Option.objects.filter(has_parameters=True).count()}'
            )

    def import_parameter_prices(self):
        """Импорт цен модификаторов параметров"""
        self.stdout.write('\n3. Импорт цен параметров...')
        
        # Получаем Махачкалу как базовый город
        try:
            makhachkala = City.objects.get(id=1)
        except City.DoesNotExist:
            self.stdout.write(self.style.WARNING(
                '   Город с id=1 не найден, используем первый активный город'
            ))
            makhachkala = City.objects.filter(is_active=True).first()
        
        if not makhachkala:
            self.stdout.write(self.style.ERROR('   Нет активных городов'))
            return
        
        # Модификаторы цен для радиусов шин
        # (данные из анализа дампа приложения)
        radius_modifiers = {
            'R13': 0,
            'R14': 0,
            'R15': 100,
            'R16': 100,
            'R17': 200,
            'R18': 300,
            'R19': 500,
            'R20': 700,
            'R21': 900,
            'R22': 1200,
        }
        
        # Получаем опции с параметром радиуса
        tire_radius = ParameterType.objects.filter(code='tire_radius').first()
        if not tire_radius:
            self.stdout.write(self.style.WARNING(
                '   Тип параметра tire_radius не найден'
            ))
            return
        
        options_with_radius = Option.objects.filter(
            parameter_types__parameter_type=tire_radius
        ).distinct()
        
        created_count = 0
        
        for option in options_with_radius:
            for radius_value, modifier in radius_modifiers.items():
                try:
                    param_value = ParameterValue.objects.get(
                        parameter_type=tire_radius,
                        value=radius_value
                    )
                except ParameterValue.DoesNotExist:
                    continue
                
                if self.dry_run:
                    self.stdout.write(
                        f'  [DRY] {option.title} + {radius_value} в {makhachkala.title}: +{modifier} ₽'
                    )
                    continue
                
                price, created = ParameterPrice.objects.update_or_create(
                    option=option,
                    parameter_value=param_value,
                    city=makhachkala,
                    technic_category=None,
                    defaults={'price_modifier': Decimal(str(modifier))}
                )
                
                if created:
                    created_count += 1
        
        if not self.dry_run:
            self.stdout.write(
                f'   Создано цен параметров: {created_count}'
            )
            self.stdout.write(
                f'   Всего цен параметров: {ParameterPrice.objects.count()}'
            )
        
        self.stdout.write(self.style.WARNING(
            '\n   ВАЖНО: Цены параметров импортированы только для Махачкалы.'
        ))
        self.stdout.write(self.style.WARNING(
            '   Для других городов настройте цены вручную через админку.'
        ))

