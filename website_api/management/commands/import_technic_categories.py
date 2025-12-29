"""Management command to import technic categories from SQL dump"""
from django.core.management.base import BaseCommand
from django.conf import settings
from website_api.models import TechnicCategory, Service
from website_api.management.commands.utils.sql_parser import parse_technic_categories
import os


class Command(BaseCommand):
    help = 'Import all technic categories from SQL dump'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dump-path',
            type=str,
            default='archive/911_last.sql',
            help='Path to SQL dump file'
        )

    def handle(self, *args, **options):
        dump_path = options['dump_path']
        
        # Make path absolute
        if not os.path.isabs(dump_path):
            dump_path = os.path.join(settings.BASE_DIR, dump_path)
        
        if not os.path.exists(dump_path):
            self.stdout.write(self.style.ERROR(f'Dump file not found: {dump_path}'))
            return
        
        self.stdout.write('Parsing technic categories from SQL dump...')
        categories_data = parse_technic_categories(dump_path)
        
        self.stdout.write(f'Found {len(categories_data)} categories in dump')
        
        # Get services for linking
        try:
            shinomontazh = Service.objects.get(slug='shinomontazh')
            evakuator = Service.objects.get(slug='evakuator')
        except Service.DoesNotExist:
            self.stdout.write(self.style.ERROR(
                'Services not found! Run import_services first.'
            ))
            return
        
        # Map categories to services
        # Легковой и Грузовой → Шиномонтаж и Эвакуатор
        # Остальные → только Эвакуатор
        category_service_map = {
            'Легковой автомобиль': [shinomontazh, evakuator],
            'Грузовой автомобиль': [shinomontazh, evakuator],
        }
        
        created_count = 0
        updated_count = 0
        
        for cat_data in categories_data:
            cat_id = cat_data['id']
            title = cat_data['title']
            
            # Determine which services this category applies to
            services_for_cat = category_service_map.get(title, [evakuator])
            
            for service in services_for_cat:
                category, created = TechnicCategory.objects.get_or_create(
                    title=title,
                    service=service
                )
                
                if created:
                    created_count += 1
                    self.stdout.write(f'  ✓ Created: {title} → {service.title}')
                else:
                    updated_count += 1
        
        self.stdout.write(self.style.SUCCESS(
            f'\n✓ Successfully imported technic categories!'
        ))
        self.stdout.write(f'  Created: {created_count}')
        self.stdout.write(f'  Updated: {updated_count}')
        self.stdout.write(f'  Total: {TechnicCategory.objects.count()}')

