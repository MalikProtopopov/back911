"""Management command to generate SEO metadata for all pages"""
from django.core.management.base import BaseCommand
from website_api.models import Service, City, SeoMeta
import json


class Command(BaseCommand):
    help = 'Generate SEO metadata for all pages using formulas'

    def add_arguments(self, parser):
        parser.add_argument(
            '--regenerate',
            action='store_true',
            help='Regenerate existing SEO metadata'
        )

    def handle(self, *args, **options):
        regenerate = options['regenerate']
        
        created_count = 0
        updated_count = 0
        skipped_count = 0
        
        # 1. Home page SEO
        self.stdout.write('Generating home page SEO...')
        home_seo, created = SeoMeta.objects.update_or_create(
            page_type='home',
            full_slug='/',
            defaults={
                'title': '911 - Экстренные автоуслуги в России | Эвакуатор, Шиномонтаж, Техпомощь',
                'meta_description': 'Платформа экстренных автоуслуг 911. Эвакуатор, шиномонтаж, заправка в 82 городах России. Работаем 24/7. Быстрый выезд.',
                'h1_title': 'Экстренные автоуслуги 911',
                'meta_keywords': 'экстренная помощь на дороге, эвакуатор, шиномонтаж, заправка, техпомощь',
                'og_title': '911 - Экстренные автоуслуги в России',
                'og_description': 'Быстрая помощь на дороге. Эвакуатор, шиномонтаж, заправка. Работаем в 82 городах.',
                'schema_json': {
                    "@context": "https://schema.org",
                    "@type": "WebSite",
                    "name": "911",
                    "url": "https://911.ru/",
                    "description": "Платформа экстренных автомобильных услуг"
                },
                'is_active': True
            }
        )
        if created:
            created_count += 1
        
        # 2. City pages SEO
        self.stdout.write('\nGenerating city pages SEO...')
        cities = City.objects.filter(is_active=True)
        
        for city in cities:
            slug = f'/{city.slug}/'
            
            existing = SeoMeta.objects.filter(
                page_type='city',
                full_slug=slug
            ).first()
            
            if existing and not regenerate:
                skipped_count += 1
                continue
            
            seo_data = {
                'page_type': 'city',
                'city': city,
                'full_slug': slug,
                'title': f'Автоуслуги в {city.title} - Эвакуатор, Шиномонтаж 24/7 | 911',
                'meta_description': f'Экстренные автоуслуги в {city.title}: эвакуатор, шиномонтаж, техпомощь на дороге. Быстрый выезд. Работаем круглосуточно.',
                'h1_title': f'Автоуслуги в {city.title}',
                'meta_keywords': f'автоуслуги {city.title}, эвакуатор {city.title}, шиномонтаж {city.title}',
                'og_title': f'Автоуслуги в {city.title} | 911',
                'og_description': f'Эвакуатор, шиномонтаж, техпомощь в {city.title}. Работаем 24/7.',
                'schema_json': {
                    "@context": "https://schema.org",
                    "@type": "LocalBusiness",
                    "name": f"911 в {city.title}",
                    "address": {
                        "@type": "PostalAddress",
                        "addressLocality": city.title
                    }
                },
                'is_active': True
            }
            
            if existing:
                for key, value in seo_data.items():
                    setattr(existing, key, value)
                existing.save()
                updated_count += 1
            else:
                SeoMeta.objects.create(**seo_data)
                created_count += 1
        
        # 3. Service pages SEO
        self.stdout.write('\nGenerating service pages SEO...')
        services = Service.objects.filter(is_active=True)
        
        service_names = {
            'shinomontazh': 'Выездной шиномонтаж',
            'evakuator': 'Эвакуатор',
            'zapravka-toplivom': 'Доставка топлива',
            'avtovyshka': 'Автовышка'
        }
        
        for service in services:
            slug = f'/{service.slug}/'
            service_name = service_names.get(service.slug, service.title)
            
            existing = SeoMeta.objects.filter(
                page_type='service',
                full_slug=slug
            ).first()
            
            if existing and not regenerate:
                skipped_count += 1
                continue
            
            seo_data = {
                'page_type': 'service',
                'service': service,
                'full_slug': slug,
                'title': f'{service_name} - Заказать онлайн в 82 городах России | 911',
                'meta_description': f'{service_name} с быстрым выездом. Работаем в 82 городах России. Профессиональные мастера. Гарантия качества.',
                'h1_title': f'{service_name} по России',
                'meta_keywords': f'{service_name}, заказать {service_name}, {service_name} цена',
                'og_title': f'{service_name} | 911',
                'og_description': f'{service_name} в 82 городах России. Работаем 24/7.',
                'schema_json': {
                    "@context": "https://schema.org",
                    "@type": "Service",
                    "name": service_name,
                    "provider": {
                        "@type": "Organization",
                        "name": "911"
                    }
                },
                'is_active': True
            }
            
            if existing:
                for key, value in seo_data.items():
                    setattr(existing, key, value)
                existing.save()
                updated_count += 1
            else:
                SeoMeta.objects.create(**seo_data)
                created_count += 1
        
        # 4. City + Service pages SEO
        self.stdout.write('\nGenerating city-service pages SEO...')
        
        for city in cities:
            for service in services:
                slug = f'/{city.slug}/{service.slug}/'
                service_name = service_names.get(service.slug, service.title)
                
                # Lowercase service name for description
                service_lower = service_name.lower()
                
                existing = SeoMeta.objects.filter(
                    page_type='city_service',
                    full_slug=slug
                ).first()
                
                if existing and not regenerate:
                    skipped_count += 1
                    continue
                
                seo_data = {
                    'page_type': 'city_service',
                    'city': city,
                    'service': service,
                    'full_slug': slug,
                    'title': f'{service_name} в {city.title} - Быстро и недорого | 911',
                    'meta_description': f'Заказать {service_lower} в {city.title} онлайн. Выезд мастера за 20-30 минут. Прозрачные цены. Работаем 24/7.',
                    'h1_title': f'{service_name} в {city.title}',
                    'meta_keywords': f'{service_lower}, {service_lower} {city.title}, заказать {service_lower}, {service_lower} цена {city.title}',
                    'og_title': f'{service_name} в {city.title} | 911',
                    'og_description': f'{service_name} в {city.title}. Быстрый выезд. Доступные цены.',
                    'schema_json': {
                        "@context": "https://schema.org",
                        "@type": "Service",
                        "name": f"{service_name} в {city.title}",
                        "provider": {
                            "@type": "Organization",
                            "name": "911"
                        },
                        "areaServed": {
                            "@type": "City",
                            "name": city.title
                        },
                        "availableChannel": {
                            "@type": "ServiceChannel",
                            "serviceUrl": f"https://911.ru{slug}"
                        }
                    },
                    'is_active': True
                }
                
                if existing:
                    for key, value in seo_data.items():
                        setattr(existing, key, value)
                    existing.save()
                    updated_count += 1
                else:
                    SeoMeta.objects.create(**seo_data)
                    created_count += 1
        
        self.stdout.write(self.style.SUCCESS(
            f'\n✓ Successfully generated SEO metadata!'
        ))
        self.stdout.write(f'  Created: {created_count}')
        self.stdout.write(f'  Updated: {updated_count}')
        self.stdout.write(f'  Skipped: {skipped_count}')
        self.stdout.write(f'  Total: {SeoMeta.objects.count()}')
