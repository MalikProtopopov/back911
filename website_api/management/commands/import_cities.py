"""Management command to import cities from SQL dump"""
from django.core.management.base import BaseCommand
from django.conf import settings
from website_api.models import City
from website_api.management.commands.utils.sql_parser import parse_cities, transliterate
import os


class Command(BaseCommand):
    help = 'Import all cities from SQL dump'

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
        
        self.stdout.write('Parsing cities from SQL dump...')
        cities_data = parse_cities(dump_path)
        
        self.stdout.write(f'Found {len(cities_data)} cities in dump')
        
        created_count = 0
        updated_count = 0
        
        for idx, city_data in enumerate(cities_data, 1):
            city_id = city_data['id']
            title = city_data['title']
            slug = transliterate(title)
            
            city, created = City.objects.update_or_create(
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
            f'\n✓ Successfully imported cities!'
        ))
        self.stdout.write(f'  Created: {created_count}')
        self.stdout.write(f'  Updated: {updated_count}')
        self.stdout.write(f'  Total: {City.objects.count()}')

