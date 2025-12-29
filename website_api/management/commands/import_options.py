"""Management command to import options from SQL dump"""
from django.core.management.base import BaseCommand
from django.conf import settings
from website_api.models import Option, Service
from website_api.management.commands.utils.sql_parser import parse_options
import os


class Command(BaseCommand):
    help = 'Import all options from SQL dump'

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
        
        self.stdout.write('Parsing options from SQL dump...')
        options_data = parse_options(dump_path)
        
        self.stdout.write(f'Found {len(options_data)} options in dump')
        
        # Get services mapping (ID from dump -> Django service)
        services_map = {}
        for service in Service.objects.all():
            # Map by ID from dump (1, 2, 3, 4)
            # This assumes IDs match between dump and our DB
            services_map[service.id] = service
        
        if not services_map:
            self.stdout.write(self.style.ERROR(
                'No services found! Run import_services first.'
            ))
            return
        
        created_count = 0
        updated_count = 0
        skipped_count = 0
        
        for opt_data in options_data:
            opt_id = opt_data['id']
            title = opt_data['title']
            service_id = opt_data['service_id']
            
            # Get corresponding service
            service = services_map.get(service_id)
            
            if not service:
                skipped_count += 1
                self.stdout.write(self.style.WARNING(
                    f'  ⚠ Skipped: {title} (service_id={service_id} not found)'
                ))
                continue
            
            option, created = Option.objects.update_or_create(
                title=title,
                service=service,
                defaults={
                    'is_active': True
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(f'  ✓ Created: {title} → {service.title}')
            else:
                updated_count += 1
        
        self.stdout.write(self.style.SUCCESS(
            f'\n✓ Successfully imported options!'
        ))
        self.stdout.write(f'  Created: {created_count}')
        self.stdout.write(f'  Updated: {updated_count}')
        self.stdout.write(f'  Skipped: {skipped_count}')
        self.stdout.write(f'  Total: {Option.objects.count()}')

