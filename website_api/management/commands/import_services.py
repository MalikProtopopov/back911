"""Management command to import services from SQL dump"""
from django.core.management.base import BaseCommand
from django.conf import settings
from website_api.models import Service
from website_api.management.commands.utils.sql_parser import parse_services, transliterate
import os


class Command(BaseCommand):
    help = 'Import all services from SQL dump'

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
        
        self.stdout.write('Parsing services from SQL dump...')
        services_data = parse_services(dump_path)
        
        self.stdout.write(f'Found {len(services_data)} services in dump')
        
        # Manual slug mapping for better SEO
        slug_map = {
            'Выездной шиномонтаж': 'shinomontazh',
            'Доставка топлива': 'zapravka-toplivom',
            'Эвакуатор / манипулятор': 'evakuator',
            'Автовышка': 'avtovyshka'
        }
        
        created_count = 0
        updated_count = 0
        
        for idx, service_data in enumerate(services_data, 1):
            service_id = service_data['id']
            title = service_data['title']
            
            # Use manual slug if available, otherwise transliterate
            slug = slug_map.get(title, transliterate(title))
            
            service, created = Service.objects.update_or_create(
                title=title,
                defaults={
                    'slug': slug,
                    'is_active': True,
                    'display_order': idx
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(f'  ✓ Created: {title} ({slug})')
            else:
                updated_count += 1
                self.stdout.write(f'  ↻ Updated: {title} ({slug})')
        
        self.stdout.write(self.style.SUCCESS(
            f'\n✓ Successfully imported services!'
        ))
        self.stdout.write(f'  Created: {created_count}')
        self.stdout.write(f'  Updated: {updated_count}')
        self.stdout.write(f'  Total: {Service.objects.count()}')

