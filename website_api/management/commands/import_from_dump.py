"""
Management command to import data from SQL dump.
This command parses the 911_last.sql dump file and creates fixture data.
"""
import json
import os
import re
from django.core.management.base import BaseCommand
from slugify import slugify as russian_slugify


class Command(BaseCommand):
    help = 'Import cities, services, options, and prices from SQL dump'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dump-file',
            default='archive/911_last.sql',
            help='Path to SQL dump file'
        )
        parser.add_argument(
            '--output-dir',
            default='website_api/fixtures',
            help='Output directory for fixtures'
        )

    def handle(self, *args, **options):
        dump_file = options['dump_file']
        output_dir = options['output_dir']

        self.stdout.write(f'Reading dump file: {dump_file}')
        
        if not os.path.exists(dump_file):
            self.stderr.write(self.style.ERROR(f'Dump file not found: {dump_file}'))
            return

        with open(dump_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Parse data
        cities = self.parse_cities(content)
        services = self.parse_services(content)
        options = self.parse_options(content)
        technic_categories = self.parse_technic_categories(content)
        option_prices = self.parse_option_prices(content)

        self.stdout.write(f'Found {len(cities)} cities')
        self.stdout.write(f'Found {len(services)} services')
        self.stdout.write(f'Found {len(options)} options')
        self.stdout.write(f'Found {len(technic_categories)} technic categories')
        self.stdout.write(f'Found {len(option_prices)} option prices')

        # Generate fixtures
        os.makedirs(output_dir, exist_ok=True)

        # Cities fixture
        cities_fixture = self.generate_cities_fixture(cities)
        self.write_fixture(f'{output_dir}/cities.json', cities_fixture)

        # Services fixture
        services_fixture = self.generate_services_fixture(services)
        self.write_fixture(f'{output_dir}/services.json', services_fixture)

        # Technic categories fixture
        technic_fixture = self.generate_technic_fixture(technic_categories, services)
        self.write_fixture(f'{output_dir}/technic_categories.json', technic_fixture)

        # Options fixture
        options_fixture = self.generate_options_fixture(options)
        self.write_fixture(f'{output_dir}/options.json', options_fixture)

        # Option prices fixture (sample)
        prices_fixture = self.generate_prices_fixture(option_prices, cities, options, technic_categories)
        self.write_fixture(f'{output_dir}/option_prices.json', prices_fixture)

        self.stdout.write(self.style.SUCCESS('Import completed successfully!'))

    def parse_cities(self, content):
        """Parse cities from COPY public.city_db"""
        cities = {}
        pattern = r'COPY public\.city_db \(id, title\) FROM stdin;(.*?)\\.'
        match = re.search(pattern, content, re.DOTALL)
        if match:
            data = match.group(1).strip()
            for line in data.split('\n'):
                if line.strip():
                    parts = line.split('\t')
                    if len(parts) >= 2:
                        city_id = int(parts[0])
                        title = parts[1].strip()
                        cities[city_id] = title
        return cities

    def parse_services(self, content):
        """Parse services from COPY public.service_db"""
        services = {}
        pattern = r'COPY public\.service_db \(id, title\) FROM stdin;(.*?)\\.'
        match = re.search(pattern, content, re.DOTALL)
        if match:
            data = match.group(1).strip()
            for line in data.split('\n'):
                if line.strip():
                    parts = line.split('\t')
                    if len(parts) >= 2:
                        service_id = int(parts[0])
                        title = parts[1].strip()
                        services[service_id] = title
        return services

    def parse_options(self, content):
        """Parse options from COPY public.option_db"""
        options = {}
        pattern = r'COPY public\.option_db \(id, title, service_id\) FROM stdin;(.*?)\\.'
        match = re.search(pattern, content, re.DOTALL)
        if match:
            data = match.group(1).strip()
            for line in data.split('\n'):
                if line.strip():
                    parts = line.split('\t')
                    if len(parts) >= 3:
                        option_id = int(parts[0])
                        title = parts[1].strip()
                        service_id = int(parts[2])
                        options[option_id] = {
                            'title': title,
                            'service_id': service_id
                        }
        return options

    def parse_technic_categories(self, content):
        """Parse technic categories from COPY public.technic_category_db"""
        categories = {}
        pattern = r'COPY public\.technic_category_db \(id, title\) FROM stdin;(.*?)\\.'
        match = re.search(pattern, content, re.DOTALL)
        if match:
            data = match.group(1).strip()
            for line in data.split('\n'):
                if line.strip():
                    parts = line.split('\t')
                    if len(parts) >= 2:
                        cat_id = int(parts[0])
                        title = parts[1].strip()
                        categories[cat_id] = title
        return categories

    def parse_option_prices(self, content):
        """Parse option prices from COPY public.option_price_db"""
        prices = []
        pattern = r'COPY public\.option_price_db \(id, amount, city_id, option_id, technic_category_id\) FROM stdin;(.*?)\\.'
        match = re.search(pattern, content, re.DOTALL)
        if match:
            data = match.group(1).strip()
            for line in data.split('\n'):
                if line.strip():
                    parts = line.split('\t')
                    if len(parts) >= 5:
                        price_id = int(parts[0])
                        amount = parts[1].strip()
                        city_id = int(parts[2])
                        option_id = int(parts[3])
                        tech_cat_id = parts[4].strip()
                        if tech_cat_id == '\\N':
                            tech_cat_id = None
                        else:
                            tech_cat_id = int(tech_cat_id)
                        prices.append({
                            'id': price_id,
                            'amount': amount,
                            'city_id': city_id,
                            'option_id': option_id,
                            'technic_category_id': tech_cat_id
                        })
        return prices

    def generate_cities_fixture(self, cities):
        """Generate cities fixture"""
        # Major cities first
        major_cities = ['Москва', 'Санкт Петербург', 'Казань', 'Краснодар', 
                       'Екатеринбург', 'Новосибирск', 'Нижний Новгород']
        
        fixture = []
        display_order = 1
        
        # Sort cities: major cities first, then alphabetically
        sorted_cities = sorted(cities.items(), key=lambda x: (
            x[1] not in major_cities,
            major_cities.index(x[1]) if x[1] in major_cities else 999,
            x[1]
        ))
        
        for city_id, title in sorted_cities:
            slug = russian_slugify(title)
            fixture.append({
                "model": "website_api.city",
                "pk": city_id,
                "fields": {
                    "title": title,
                    "slug": slug,
                    "is_active": True,
                    "display_order": display_order
                }
            })
            display_order += 1
        
        return fixture

    def generate_services_fixture(self, services):
        """Generate services fixture with optimized slugs"""
        slug_map = {
            'Выездной шиномонтаж': 'shinomontazh',
            'Доставка топлива': 'dostavka-topliva',
            'Эвакуатор / манипулятор': 'evakuator',
            'Автовышка': 'avtovyshka'
        }
        
        fixture = []
        display_order = 1
        
        for service_id, title in sorted(services.items()):
            slug = slug_map.get(title, russian_slugify(title))
            fixture.append({
                "model": "website_api.service",
                "pk": service_id,
                "fields": {
                    "title": title,
                    "slug": slug,
                    "is_active": True,
                    "display_order": display_order
                }
            })
            display_order += 1
        
        return fixture

    def generate_technic_fixture(self, technic_categories, services):
        """Generate technic categories fixture"""
        # Map categories to services based on business logic
        # Шиномонтаж and Эвакуатор use vehicle categories
        service_categories = {
            1: [3, 4],  # Шиномонтаж: Грузовой, Легковой
            2: [4, 5],  # Доставка топлива: Легковой, Генератор
            3: [3, 4],  # Эвакуатор: Грузовой, Легковой
            4: [],  # Автовышка: no categories
        }
        
        fixture = []
        pk = 1
        
        for service_id, cat_ids in service_categories.items():
            for cat_id in cat_ids:
                if cat_id in technic_categories:
                    fixture.append({
                        "model": "website_api.techniccategory",
                        "pk": pk,
                        "fields": {
                            "title": technic_categories[cat_id],
                            "service_id": service_id
                        }
                    })
                    pk += 1
        
        return fixture

    def generate_options_fixture(self, options):
        """Generate options fixture"""
        fixture = []
        
        for option_id, data in sorted(options.items()):
            fixture.append({
                "model": "website_api.option",
                "pk": option_id,
                "fields": {
                    "title": data['title'],
                    "service_id": data['service_id'],
                    "is_active": True
                }
            })
        
        return fixture

    def generate_prices_fixture(self, prices, cities, options, technic_categories):
        """Generate option prices fixture (limited sample for initial data)"""
        fixture = []
        
        # Only include prices for active options in major cities
        major_city_ids = [city_id for city_id, title in cities.items() 
                        if title in ['Москва', 'Санкт Петербург', 'Казань', 'Краснодар']]
        
        seen = set()
        pk = 1
        
        for price in prices:
            city_id = price['city_id']
            option_id = price['option_id']
            tech_cat_id = price['technic_category_id']
            
            # Skip if city or option doesn't exist
            if city_id not in cities or option_id not in options:
                continue
            
            # Create unique key
            key = (option_id, city_id, tech_cat_id)
            if key in seen:
                continue
            seen.add(key)
            
            # For initial load, include all prices but sample for large cities
            if city_id in major_city_ids or len(fixture) < 500:
                fixture.append({
                    "model": "website_api.optionprice",
                    "pk": pk,
                    "fields": {
                        "option_id": option_id,
                        "city_id": city_id,
                        "technic_category_id": tech_cat_id,
                        "amount": price['amount']
                    }
                })
                pk += 1
        
        return fixture

    def write_fixture(self, filepath, data):
        """Write fixture to JSON file"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        self.stdout.write(f'Written: {filepath}')

