"""
Команда для полного импорта данных из SQL дампа.

Импортирует:
- Города
- Услуги  
- Категории техники
- Опции (с флагом has_parameters)
- Типы параметров (tire_radius, fuel_type)
- Значения параметров (R13-R23, АИ-92, АИ-95...)
- Связи опций с параметрами (OptionParameterType)
- Цены опций (OptionPrice)
- Цены параметров (ParameterPrice)
- Зоны доставки (DeliveryZone)

Использование:
    python manage.py import_full_data --dump-file archive/911_last.sql
    python manage.py import_full_data --dump-file archive/911_last.sql --dry-run
"""
from decimal import Decimal
from collections import defaultdict

from django.core.management.base import BaseCommand
from django.db import transaction

from website_api.models import (
    City, Service, TechnicCategory, Option, OptionPrice,
    ParameterType, ParameterValue, OptionParameterType,
    ParameterPrice, DeliveryZone
)
from website_api.management.commands.utils.sql_parser import (
    parse_cities, parse_services, parse_technic_categories,
    parse_options, parse_prices, parse_order_conditions,
    parse_working_zones
)


class Command(BaseCommand):
    help = 'Импорт полных данных из SQL дампа'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dump-file',
            type=str,
            required=True,
            help='Путь к SQL дампу'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Показать что будет импортировано, не применяя изменений'
        )

    def handle(self, *args, **options):
        dump_path = options['dump_file']
        dry_run = options['dry_run']

        self.stdout.write(f'Читаем дамп: {dump_path}')

        # Парсим все данные
        self.stdout.write('Парсинг данных...')
        
        raw_cities = parse_cities(dump_path)
        raw_services = parse_services(dump_path)
        raw_categories = parse_technic_categories(dump_path)
        raw_options = parse_options(dump_path)
        raw_prices = parse_prices(dump_path)
        raw_conditions = parse_order_conditions(dump_path)
        raw_zones = parse_working_zones(dump_path)

        self.stdout.write(f'  Города: {len(raw_cities)}')
        self.stdout.write(f'  Услуги: {len(raw_services)}')
        self.stdout.write(f'  Категории техники: {len(raw_categories)}')
        self.stdout.write(f'  Опции: {len(raw_options)}')
        self.stdout.write(f'  Цены опций: {len(raw_prices)}')
        self.stdout.write(f'  Условия (параметры): {len(raw_conditions)}')
        self.stdout.write(f'  Зоны доставки: {len(raw_zones)}')

        if dry_run:
            self._dry_run_report(
                raw_cities, raw_services, raw_categories,
                raw_options, raw_prices, raw_conditions, raw_zones
            )
            return

        # Импорт с транзакцией
        with transaction.atomic():
            # 1. Города
            city_map = self._import_cities(raw_cities)
            
            # 2. Услуги
            service_map = self._import_services(raw_services)
            
            # 3. Категории техники
            category_map = self._import_categories(raw_categories)
            
            # 4. Анализ параметров
            parameter_analysis = self._analyze_parameters(raw_conditions)
            
            # 5. Типы параметров
            param_type_map = self._import_parameter_types(parameter_analysis)
            
            # 6. Значения параметров
            param_value_map = self._import_parameter_values(parameter_analysis, param_type_map)
            
            # 7. Опции с флагом has_parameters
            option_map = self._import_options(raw_options, service_map, raw_conditions)
            
            # 8. Связи опций с параметрами
            self._import_option_parameter_types(raw_conditions, option_map, param_type_map)
            
            # 9. Цены опций
            self._import_option_prices(raw_prices, option_map, city_map, category_map)
            
            # 10. Цены параметров
            self._import_parameter_prices(raw_conditions, option_map, param_value_map, city_map)
            
            # 11. Зоны доставки
            self._import_delivery_zones(raw_zones, city_map)

        self.stdout.write(self.style.SUCCESS('\n✅ Импорт завершён успешно!'))
        self._final_report()

    def _dry_run_report(self, cities, services, categories, options, prices, conditions, zones):
        """Отчёт о том, что будет импортировано"""
        self.stdout.write('\n' + '=' * 60)
        self.stdout.write('DRY RUN - Данные не будут записаны')
        self.stdout.write('=' * 60)
        
        # Анализ параметров
        param_types = set()
        param_values = defaultdict(set)
        
        for cond in conditions:
            ctype = cond['condition_type']
            param_types.add(ctype)
            param_values[ctype].add(cond['title'])
        
        self.stdout.write('\n📋 Типы параметров:')
        for pt in sorted(param_types):
            values = sorted(param_values[pt])
            self.stdout.write(f'  - {pt}: {", ".join(values)}')
        
        # Опции с параметрами
        options_with_params = set()
        for cond in conditions:
            if cond['option_id']:
                options_with_params.add(cond['option_id'])
        
        self.stdout.write(f'\n📋 Опции с параметрами: {len(options_with_params)}')
        
        # Зоны доставки по городам
        zones_by_city = defaultdict(list)
        for zone in zones:
            if zone['city_id']:
                zones_by_city[zone['city_id']].append(zone)
        
        self.stdout.write(f'\n📋 Городов с зонами доставки: {len(zones_by_city)}')
        
        self.stdout.write('\n' + '=' * 60)
        self.stdout.write('Запустите без --dry-run для импорта')
        self.stdout.write('=' * 60)

    def _import_cities(self, raw_cities):
        """Импорт городов"""
        self.stdout.write('\n1. Импорт городов...')
        city_map = {}  # old_id -> new City
        
        for raw in raw_cities:
            city, created = City.objects.get_or_create(
                title=raw['title'],
                defaults={'slug': self._slugify(raw['title'])}
            )
            city_map[raw['id']] = city
            if created:
                self.stdout.write(f'   + {city.title}')
        
        self.stdout.write(f'   Всего городов: {City.objects.count()}')
        return city_map

    def _import_services(self, raw_services):
        """Импорт услуг"""
        self.stdout.write('\n2. Импорт услуг...')
        service_map = {}  # old_id -> new Service
        
        for raw in raw_services:
            service, created = Service.objects.get_or_create(
                title=raw['title'],
                defaults={'slug': self._slugify(raw['title'])}
            )
            service_map[raw['id']] = service
            if created:
                self.stdout.write(f'   + {service.title}')
        
        self.stdout.write(f'   Всего услуг: {Service.objects.count()}')
        return service_map

    def _import_categories(self, raw_categories):
        """Импорт категорий техники"""
        self.stdout.write('\n3. Импорт категорий техники...')
        category_map = {}  # old_id -> new TechnicCategory
        
        for raw in raw_categories:
            category, created = TechnicCategory.objects.get_or_create(
                title=raw['title'],
                defaults={'slug': self._slugify(raw['title'])}
            )
            category_map[raw['id']] = category
            if created:
                self.stdout.write(f'   + {category.title}')
        
        self.stdout.write(f'   Всего категорий: {TechnicCategory.objects.count()}')
        return category_map

    def _analyze_parameters(self, raw_conditions):
        """Анализ типов и значений параметров"""
        self.stdout.write('\n4. Анализ параметров...')
        
        param_types = {}  # condition_type -> {title, values}
        
        for cond in raw_conditions:
            ctype = cond['condition_type']
            if ctype not in param_types:
                param_types[ctype] = {
                    'code': ctype,
                    'title': self._get_param_title(ctype),
                    'values': set()
                }
            param_types[ctype]['values'].add(cond['title'])
        
        for code, data in param_types.items():
            self.stdout.write(f'   {data["title"]} ({code}): {len(data["values"])} значений')
        
        return param_types

    def _get_param_title(self, code):
        """Получить человекочитаемое название параметра"""
        titles = {
            'radius': 'Радиус шины',
            'fuel_type': 'Тип топлива',
            'oil_type': 'Тип масла',
            'boom_height': 'Высота автовышки',
        }
        return titles.get(code, code.replace('_', ' ').title())

    def _import_parameter_types(self, parameter_analysis):
        """Импорт типов параметров"""
        self.stdout.write('\n5. Импорт типов параметров...')
        param_type_map = {}  # code -> ParameterType
        
        for code, data in parameter_analysis.items():
            param_type, created = ParameterType.objects.get_or_create(
                code=code,
                defaults={
                    'title': data['title'],
                    'is_active': True
                }
            )
            param_type_map[code] = param_type
            if created:
                self.stdout.write(f'   + {param_type.title} ({code})')
        
        return param_type_map

    def _import_parameter_values(self, parameter_analysis, param_type_map):
        """Импорт значений параметров"""
        self.stdout.write('\n6. Импорт значений параметров...')
        param_value_map = {}  # (code, value) -> ParameterValue
        
        for code, data in parameter_analysis.items():
            param_type = param_type_map[code]
            sorted_values = self._sort_param_values(code, data['values'])
            
            for sort_order, raw_value in enumerate(sorted_values):
                # Форматируем значение для отображения
                display_name = self._format_display_value(code, raw_value)
                technical_value = self._format_technical_value(code, raw_value)
                
                param_value, created = ParameterValue.objects.get_or_create(
                    parameter_type=param_type,
                    value=technical_value,
                    defaults={
                        'display_name': display_name,
                        'sort_order': sort_order,
                        'is_active': True
                    }
                )
                param_value_map[(code, raw_value)] = param_value
                if created:
                    self.stdout.write(f'   + {param_type.code}: {display_name}')
        
        return param_value_map

    def _sort_param_values(self, code, values):
        """Сортировка значений параметров"""
        if code == 'radius':
            # Числовая сортировка для радиусов
            return sorted(values, key=lambda x: int(x) if x.isdigit() else 0)
        elif code == 'fuel_type':
            # Фиксированный порядок для топлива
            order = {'АИ-92': 0, 'АИ-95': 1, 'АИ-100': 2, 'ДТ': 3}
            return sorted(values, key=lambda x: order.get(x, 99))
        else:
            return sorted(values)

    def _format_display_value(self, code, raw_value):
        """Форматировать значение для отображения"""
        if code == 'radius':
            return f'R{raw_value}'
        return raw_value

    def _format_technical_value(self, code, raw_value):
        """Форматировать техническое значение"""
        if code == 'radius':
            return f'r{raw_value}'
        elif code == 'fuel_type':
            # АИ-92 -> ai92
            fuel_map = {
                'АИ-92': 'ai92',
                'АИ-95': 'ai95',
                'АИ-100': 'ai100',
                'ДТ': 'dt'
            }
            return fuel_map.get(raw_value, raw_value.lower())
        return raw_value.lower().replace(' ', '_')

    def _import_options(self, raw_options, service_map, raw_conditions):
        """Импорт опций с флагом has_parameters"""
        self.stdout.write('\n7. Импорт опций...')
        option_map = {}  # old_id -> Option
        
        # Собираем ID опций, у которых есть параметры
        options_with_params = set()
        for cond in raw_conditions:
            if cond['option_id']:
                options_with_params.add(cond['option_id'])
        
        for raw in raw_options:
            service = service_map.get(raw['service_id'])
            if not service:
                continue
            
            has_params = raw['id'] in options_with_params
            
            option, created = Option.objects.get_or_create(
                title=raw['title'],
                service=service,
                defaults={
                    'has_parameters': has_params,
                    'is_active': True
                }
            )
            
            # Обновляем has_parameters если опция уже существовала
            if not created and option.has_parameters != has_params:
                option.has_parameters = has_params
                option.save()
            
            option_map[raw['id']] = option
            if created:
                params_mark = ' [+params]' if has_params else ''
                self.stdout.write(f'   + {option.title}{params_mark}')
        
        self.stdout.write(f'   Всего опций: {Option.objects.count()}')
        self.stdout.write(f'   Опций с параметрами: {Option.objects.filter(has_parameters=True).count()}')
        return option_map

    def _import_option_parameter_types(self, raw_conditions, option_map, param_type_map):
        """Импорт связей опций с типами параметров"""
        self.stdout.write('\n8. Импорт связей опций с параметрами...')
        
        # Собираем уникальные связи option_id -> condition_type
        links = set()
        for cond in raw_conditions:
            if cond['option_id'] and cond['option_id'] in option_map:
                links.add((cond['option_id'], cond['condition_type']))
        
        created_count = 0
        for old_option_id, ctype in links:
            option = option_map.get(old_option_id)
            param_type = param_type_map.get(ctype)
            
            if option and param_type:
                _, created = OptionParameterType.objects.get_or_create(
                    option=option,
                    parameter_type=param_type,
                    defaults={'is_required': True}
                )
                if created:
                    created_count += 1
        
        self.stdout.write(f'   Создано связей: {created_count}')

    def _import_option_prices(self, raw_prices, option_map, city_map, category_map):
        """Импорт базовых цен опций"""
        self.stdout.write('\n9. Импорт цен опций...')
        created_count = 0
        
        for raw in raw_prices:
            option = option_map.get(raw['option_id'])
            city = city_map.get(raw['city_id'])
            
            if not option or not city:
                continue
            
            category = None
            if raw['technic_category_id']:
                category = category_map.get(raw['technic_category_id'])
            
            amount = Decimal(raw['amount'])
            
            option_price, created = OptionPrice.objects.get_or_create(
                option=option,
                city=city,
                technic_category=category,
                defaults={'amount': amount}
            )
            
            if created:
                created_count += 1
        
        self.stdout.write(f'   Создано цен: {created_count}')
        self.stdout.write(f'   Всего цен опций: {OptionPrice.objects.count()}')

    def _import_parameter_prices(self, raw_conditions, option_map, param_value_map, city_map):
        """Импорт цен параметров (надбавок)"""
        self.stdout.write('\n10. Импорт цен параметров...')
        
        # Группируем условия по опциям и ценам
        # Получаем все option_price для маппинга
        option_prices = {}
        for op in OptionPrice.objects.select_related('option', 'city'):
            key = (op.option_id, op.city_id)
            if key not in option_prices:
                option_prices[key] = []
            option_prices[key].append(op)
        
        created_count = 0
        
        for cond in raw_conditions:
            if not cond['option_id'] or cond['option_id'] not in option_map:
                continue
            
            option = option_map[cond['option_id']]
            param_value = param_value_map.get((cond['condition_type'], cond['title']))
            
            if not param_value:
                continue
            
            # Надбавка за параметр
            price_modifier = Decimal(cond['additional_price'])
            
            # Применяем ко всем городам, где есть цена на эту опцию
            for (opt_id, city_id), prices in option_prices.items():
                if opt_id != option.id:
                    continue
                
                for op in prices:
                    _, created = ParameterPrice.objects.get_or_create(
                        option=option,
                        parameter_value=param_value,
                        city=op.city,
                        technic_category=op.technic_category,
                        defaults={'price_modifier': price_modifier}
                    )
                    if created:
                        created_count += 1
        
        self.stdout.write(f'   Создано цен параметров: {created_count}')

    def _import_delivery_zones(self, raw_zones, city_map):
        """Импорт зон доставки"""
        self.stdout.write('\n11. Импорт зон доставки...')
        created_count = 0
        
        for raw in raw_zones:
            if not raw['city_id'] or raw['city_id'] not in city_map:
                continue
            
            city = city_map[raw['city_id']]
            location_status = raw['location_status']
            
            if not location_status:
                continue
            
            zone, created = DeliveryZone.objects.get_or_create(
                city=city,
                location_status=location_status,
                defaults={
                    'zone_name': raw['title'],
                    'delivery_price': Decimal(raw['departure_price']),
                    'is_active': True
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(f'   + {city.title} - {location_status}: {raw["departure_price"]} ₽')
        
        self.stdout.write(f'   Создано зон: {created_count}')
        self.stdout.write(f'   Всего зон: {DeliveryZone.objects.count()}')

    def _final_report(self):
        """Финальный отчёт"""
        self.stdout.write('\n' + '=' * 60)
        self.stdout.write('📊 ИТОГОВЫЙ ОТЧЁТ')
        self.stdout.write('=' * 60)
        self.stdout.write(f'  Города: {City.objects.count()}')
        self.stdout.write(f'  Услуги: {Service.objects.count()}')
        self.stdout.write(f'  Категории техники: {TechnicCategory.objects.count()}')
        self.stdout.write(f'  Опции: {Option.objects.count()} (с параметрами: {Option.objects.filter(has_parameters=True).count()})')
        self.stdout.write(f'  Типы параметров: {ParameterType.objects.count()}')
        self.stdout.write(f'  Значения параметров: {ParameterValue.objects.count()}')
        self.stdout.write(f'  Связи опция-параметр: {OptionParameterType.objects.count()}')
        self.stdout.write(f'  Цены опций: {OptionPrice.objects.count()}')
        self.stdout.write(f'  Цены параметров: {ParameterPrice.objects.count()}')
        self.stdout.write(f'  Зоны доставки: {DeliveryZone.objects.count()}')
        self.stdout.write('=' * 60)

    def _slugify(self, text):
        """Простая транслитерация для slug"""
        translit_map = {
            'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd',
            'е': 'e', 'ё': 'yo', 'ж': 'zh', 'з': 'z', 'и': 'i',
            'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n',
            'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't',
            'у': 'u', 'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch',
            'ш': 'sh', 'щ': 'sch', 'ъ': '', 'ы': 'y', 'ь': '',
            'э': 'e', 'ю': 'yu', 'я': 'ya',
            ' ': '-', '/': '-', '\\': '-'
        }
        
        result = []
        for char in text.lower():
            if char in translit_map:
                result.append(translit_map[char])
            elif char.isalnum() or char == '-':
                result.append(char)
        
        slug = ''.join(result)
        # Убираем множественные дефисы
        while '--' in slug:
            slug = slug.replace('--', '-')
        return slug.strip('-')

