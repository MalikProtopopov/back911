"""Management command to load initial data"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from website_api.models import City, Service, Option, TechnicCategory, OptionPrice


class Command(BaseCommand):
    help = 'Load initial data for cities, services, and options'

    def handle(self, *args, **options):
        self.stdout.write('Loading initial data...')
        
        # Create cities
        cities_data = [
            ('Москва', 'moskva', 1),
            ('Санкт-Петербург', 'sankt-peterburg', 2),
            ('Новосибирск', 'novosibirsk', 3),
            ('Екатеринбург', 'ekaterinburg', 4),
            ('Казань', 'kazan', 5),
            ('Нижний Новгород', 'nizhniy-novgorod', 6),
            ('Челябинск', 'chelyabinsk', 7),
            ('Самара', 'samara', 8),
            ('Омск', 'omsk', 9),
            ('Ростов-на-Дону', 'rostov-na-donu', 10),
        ]
        
        cities = {}
        for title, slug, order in cities_data:
            city, created = City.objects.get_or_create(
                slug=slug,
                defaults={
                    'title': title,
                    'is_active': True,
                    'display_order': order
                }
            )
            cities[slug] = city
            if created:
                self.stdout.write(f'  ✓ Created city: {title}')
        
        # Create services
        services_data = [
            ('Эвакуатор', 'evakuator', 1),
            ('Шиномонтаж', 'shinomontazh', 2),
            ('Техническая помощь', 'tehnicheskaya-pomoshch', 3),
            ('Заправка топливом', 'zapravka-toplivom', 4),
            ('Вскрытие автомобиля', 'vskrytie-avtomobilya', 5),
            ('Прикурить автомобиль', 'prikurit-avtomobil', 6),
        ]
        
        services = {}
        for title, slug, order in services_data:
            service, created = Service.objects.get_or_create(
                slug=slug,
                defaults={
                    'title': title,
                    'is_active': True,
                    'display_order': order
                }
            )
            services[slug] = service
            if created:
                self.stdout.write(f'  ✓ Created service: {title}')
        
        # Create technic categories for эвакуатор
        if 'evakuator' in services:
            evak_service = services['evakuator']
            categories_data = [
                'Легковой автомобиль',
                'Кроссовер',
                'Внедорожник',
                'Легкий коммерческий',
            ]
            
            categories = {}
            for title in categories_data:
                cat, created = TechnicCategory.objects.get_or_create(
                    service=evak_service,
                    title=title
                )
                categories[title] = cat
                if created:
                    self.stdout.write(f'  ✓ Created category: {title}')
            
            # Create evacuation options with prices
            options_data = [
                'Эвакуация до 10 км',
                'Эвакуация 10-20 км',
                'Эвакуация 20-50 км',
            ]
            
            base_prices = {
                'Легковой автомобиль': [2000, 2500, 3500],
                'Кроссовер': [2500, 3000, 4000],
                'Внедорожник': [3000, 3500, 4500],
                'Легкий коммерческий': [3500, 4000, 5000],
            }
            
            for title in options_data:
                option, created = Option.objects.get_or_create(
                    service=evak_service,
                    title=title,
                    defaults={
                        'is_active': True
                    }
                )
                
                if created:
                    self.stdout.write(f'  ✓ Created option: {title}')
                    
                    # Create prices for each category and city
                    for cat_title, prices in base_prices.items():
                        cat = categories[cat_title]
                        price_idx = options_data.index(title)
                        base_price = prices[price_idx]
                        
                        for city_slug, city in cities.items():
                            # Vary prices slightly by city
                            city_multiplier = 1.0 + (city.display_order - 1) * 0.05
                            final_price = int(base_price * city_multiplier)
                            
                            OptionPrice.objects.get_or_create(
                                option=option,
                                city=city,
                                technic_category=cat,
                                defaults={'amount': final_price}
                            )
        
        # Create tire service options
        if 'shinomontazh' in services:
            shino_service = services['shinomontazh']
            
            tire_options = [
                ('Радиус R13', 800),
                ('Радиус R14', 900),
                ('Радиус R15', 1000),
                ('Радиус R16', 1100),
                ('Радиус R17', 1200),
                ('Радиус R18', 1400),
            ]
            
            for title, base_price in tire_options:
                option, created = Option.objects.get_or_create(
                    service=shino_service,
                    title=title,
                    defaults={
                        'is_active': True
                    }
                )
                
                if created:
                    self.stdout.write(f'  ✓ Created option: {title}')
                    
                    # Create prices for each city
                    for city in cities.values():
                        city_multiplier = 1.0 + (city.display_order - 1) * 0.03
                        final_price = int(base_price * city_multiplier)
                        
                        OptionPrice.objects.get_or_create(
                            option=option,
                            city=city,
                            defaults={'amount': final_price}
                        )
        
        self.stdout.write(self.style.SUCCESS('✓ Successfully loaded all initial data!'))
        self.stdout.write(f'  Cities: {City.objects.count()}')
        self.stdout.write(f'  Services: {Service.objects.count()}')
        self.stdout.write(f'  Options: {Option.objects.count()}')
        self.stdout.write(f'  Prices: {OptionPrice.objects.count()}')

