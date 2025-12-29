"""Management command to import prices from SQL dump"""
from django.core.management.base import BaseCommand
from django.conf import settings
from website_api.models import OptionPrice, Option, City, TechnicCategory
from website_api.management.commands.utils.sql_parser import parse_prices
from decimal import Decimal
import os


class Command(BaseCommand):
    help = 'Import all option prices from SQL dump'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dump-path',
            type=str,
            default='archive/911_last.sql',
            help='Path to SQL dump file'
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=1000,
            help='Batch size for bulk create'
        )

    def handle(self, *args, **options):
        dump_path = options['dump_path']
        batch_size = options['batch_size']
        
        # Make path absolute
        if not os.path.isabs(dump_path):
            dump_path = os.path.join(settings.BASE_DIR, dump_path)
        
        if not os.path.exists(dump_path):
            self.stdout.write(self.style.ERROR(f'Dump file not found: {dump_path}'))
            return
        
        self.stdout.write('Parsing prices from SQL dump...')
        prices_data = parse_prices(dump_path)
        
        self.stdout.write(f'Found {len(prices_data)} prices in dump')
        
        # Build lookup maps for faster processing
        self.stdout.write('Building lookup maps...')
        options_map = {opt.id: opt for opt in Option.objects.all()}
        cities_map = {city.id: city for city in City.objects.all()}
        
        # For technic categories, we need to find by title and service
        # since we recreated them
        technic_categories_cache = {}
        
        created_count = 0
        updated_count = 0
        skipped_count = 0
        
        prices_to_create = []
        
        for idx, price_data in enumerate(prices_data, 1):
            if idx % 100 == 0:
                self.stdout.write(f'  Processing {idx}/{len(prices_data)}...')
            
            option_id = price_data['option_id']
            city_id = price_data['city_id']
            technic_cat_id = price_data['technic_category_id']
            amount = Decimal(price_data['amount'])
            
            # Get option and city
            option = options_map.get(option_id)
            city = cities_map.get(city_id)
            
            if not option or not city:
                skipped_count += 1
                continue
            
            # Get technic category if specified
            technic_category = None
            if technic_cat_id:
                # Try to find matching category for this service
                cache_key = (technic_cat_id, option.service.id)
                
                if cache_key not in technic_categories_cache:
                    # Find all categories for this service
                    cats = TechnicCategory.objects.filter(service=option.service)
                    technic_categories_cache[cache_key] = cats.first() if cats.exists() else None
                
                technic_category = technic_categories_cache.get(cache_key)
            
            # Check if price already exists
            existing = OptionPrice.objects.filter(
                option=option,
                city=city,
                technic_category=technic_category
            ).first()
            
            if existing:
                # Update amount if different
                if existing.amount != amount:
                    existing.amount = amount
                    existing.save()
                    updated_count += 1
            else:
                # Create new price
                prices_to_create.append(OptionPrice(
                    option=option,
                    city=city,
                    technic_category=technic_category,
                    amount=amount
                ))
                created_count += 1
                
                # Bulk create when batch is full
                if len(prices_to_create) >= batch_size:
                    OptionPrice.objects.bulk_create(prices_to_create, ignore_conflicts=True)
                    prices_to_create = []
        
        # Create remaining prices
        if prices_to_create:
            OptionPrice.objects.bulk_create(prices_to_create, ignore_conflicts=True)
        
        self.stdout.write(self.style.SUCCESS(
            f'\n✓ Successfully imported prices!'
        ))
        self.stdout.write(f'  Created: {created_count}')
        self.stdout.write(f'  Updated: {updated_count}')
        self.stdout.write(f'  Skipped: {skipped_count}')
        self.stdout.write(f'  Total: {OptionPrice.objects.count()}')

