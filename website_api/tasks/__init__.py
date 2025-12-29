from celery import shared_task
from django.core.cache import cache
from website_api.models import City, Metric


@shared_task
def update_platform_metrics():
    """Обновление платформенных метрик из нашей БД"""
    
    # Обновляем метрику городов
    total_cities = City.objects.filter(is_active=True).count()
    Metric.objects.update_or_create(
        metric_key='total_cities',
        defaults={
            'value': str(total_cities),
            'display_label': 'Городов присутствия',
            'metric_type': 'platform',
            'is_visible_on_site': True,
        }
    )
    
    return f"Updated metrics successfully"


@shared_task
def update_city_content_cache(city_id=None):
    """Обновление кешированных данных в CityContent"""
    from website_api.models import CityContent
    
    if city_id:
        cities = [City.objects.get(id=city_id)]
    else:
        cities = City.objects.all()
    
    for city in cities:
        # Инвалидировать кеш для этого города
        cache.delete(f'city_detail_{city.id}')
        cache.delete('city_list')
    
    return f"Cache updated for {len(cities)} cities"


@shared_task
def process_lead(lead_id):
    """Обработка новой заявки"""
    from website_api.models import Lead
    
    lead = Lead.objects.get(id=lead_id)
    
    # Здесь можно добавить:
    # - Отправку email уведомления
    # - Отправку в CRM
    # - Отправку в Telegram бот
    
    lead.status = 'processing'
    lead.save()
    
    return f"Lead {lead_id} processed"

