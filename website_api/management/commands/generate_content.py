"""Management command to generate HTML content for services"""
from django.core.management.base import BaseCommand
from website_api.models import Service, City, ServiceContent, CityContent


class Command(BaseCommand):
    help = 'Generate HTML content for all service-city combinations'

    def add_arguments(self, parser):
        parser.add_argument(
            '--regenerate',
            action='store_true',
            help='Regenerate existing content'
        )

    def handle(self, *args, **options):
        regenerate = options['regenerate']
        
        # HTML templates for each service
        service_templates = {
            'shinomontazh': self.get_shinomontazh_template,
            'evakuator': self.get_evakuator_template,
            'zapravka-toplivom': self.get_zapravka_template,
            'avtovyshka': self.get_avtovyshka_template,
        }
        
        services = Service.objects.filter(is_active=True)
        cities = City.objects.filter(is_active=True)
        
        self.stdout.write(f'Generating content for {services.count()} services × {cities.count()} cities...')
        
        created_count = 0
        updated_count = 0
        skipped_count = 0
        
        for service in services:
            template_func = service_templates.get(service.slug)
            
            if not template_func:
                self.stdout.write(self.style.WARNING(
                    f'  ⚠ No template for service: {service.title}'
                ))
                continue
            
            for city in cities:
                # Check if content already exists
                existing = ServiceContent.objects.filter(
                    service=service,
                    city=city
                ).first()
                
                if existing and not regenerate:
                    skipped_count += 1
                    continue
                
                # Generate HTML content
                html_content = template_func(city.title)
                
                if existing:
                    existing.description = html_content
                    existing.save()
                    updated_count += 1
                else:
                    ServiceContent.objects.create(
                        service=service,
                        city=city,
                        description=html_content,
                        meta_title=f'{service.title} в {city.title}',
                        meta_description=f'{service.title} в {city.title}. Быстро и надежно.',
                        h1_title=f'{service.title} в {city.title}'
                    )
                    created_count += 1
        
        # Also generate city-specific content
        self.stdout.write('\nGenerating city content...')
        city_created = 0
        
        for city in cities:
            if not CityContent.objects.filter(city=city).exists() or regenerate:
                html = self.get_city_template(city.title)
                CityContent.objects.update_or_create(
                    city=city,
                    defaults={
                        'short_description': f'Экстренные автоуслуги в {city.title}',
                        'full_description': html,
                        'meta_title': f'Автоуслуги в {city.title} | 911',
                        'meta_description': f'Экстренные автоуслуги в {city.title}',
                        'h1_title': f'Автоуслуги в {city.title}'
                    }
                )
                city_created += 1
        
        self.stdout.write(self.style.SUCCESS(
            f'\n✓ Successfully generated content!'
        ))
        self.stdout.write(f'  Service content created: {created_count}')
        self.stdout.write(f'  Service content updated: {updated_count}')
        self.stdout.write(f'  Service content skipped: {skipped_count}')
        self.stdout.write(f'  City content created: {city_created}')
        self.stdout.write(f'  Total service content: {ServiceContent.objects.count()}')
        self.stdout.write(f'  Total city content: {CityContent.objects.count()}')
    
    def get_shinomontazh_template(self, city_name):
        return f"""
<div class="service-intro">
  <h2>Выездной шиномонтаж в {city_name}</h2>
  <p>Профессиональный шиномонтаж с выездом в любую точку города {city_name}. 
  Работаем круглосуточно, без выходных. Приезжаем в течение 20-30 минут.</p>
</div>

<div class="service-advantages">
  <h3>Наши преимущества</h3>
  <ul>
    <li><strong>Быстрый выезд</strong> — мастер приедет за 20-30 минут</li>
    <li><strong>Профессиональное оборудование</strong> — современный шиномонтажный стенд</li>
    <li><strong>Гарантия качества</strong> — опытные мастера с многолетним стажем</li>
    <li><strong>Любой радиус колес</strong> — работаем с R13 до R22</li>
    <li><strong>Прозрачные цены</strong> — стоимость известна заранее</li>
    <li><strong>Работа 24/7</strong> — выезжаем в любое время суток</li>
  </ul>
</div>

<div class="service-pricing">
  <h3>Стоимость услуг шиномонтажа</h3>
  <p>Цены на выездной шиномонтаж в {city_name} зависят от радиуса колес и типа автомобиля. 
  Все цены указаны за одно колесо и включают демонтаж, монтаж и балансировку.</p>
  <p>Для уточнения стоимости выберите радиус ваших колес и тип автомобиля в приложении.</p>
</div>

<div class="service-how-it-works">
  <h3>Как это работает</h3>
  <ol>
    <li>Вы оставляете заявку через приложение или сайт</li>
    <li>Мастер выезжает к вам в течение 20-30 минут</li>
    <li>Производится шиномонтаж прямо на месте</li>
    <li>Вы оплачиваете услугу любым удобным способом</li>
  </ol>
</div>

<div class="service-faq">
  <h3>Часто задаваемые вопросы</h3>
  <details>
    <summary>Сколько времени занимает шиномонтаж?</summary>
    <p>В среднем 30-40 минут на все 4 колеса, включая балансировку.</p>
  </details>
  <details>
    <summary>Нужно ли снимать колеса перед приездом мастера?</summary>
    <p>Нет, мастер сделает все сам. Вам не нужно ничего подготавливать.</p>
  </details>
  <details>
    <summary>Какие колеса вы обслуживаете?</summary>
    <p>Мы работаем с колесами радиусом от R13 до R22 для легковых автомобилей и внедорожников.</p>
  </details>
  <details>
    <summary>Работаете ли вы ночью?</summary>
    <p>Да, наш сервис работает круглосуточно, 24 часа в сутки, 7 дней в неделю.</p>
  </details>
</div>
"""
    
    def get_evakuator_template(self, city_name):
        return f"""
<div class="service-intro">
  <h2>Эвакуатор в {city_name} — быстро и надежно</h2>
  <p>Услуги эвакуатора и манипулятора в {city_name}. Эвакуация легковых автомобилей, 
  внедорожников, грузовых машин и спецтехники. Работаем круглосуточно.</p>
</div>

<div class="service-advantages">
  <h3>Почему выбирают нас</h3>
  <ul>
    <li><strong>Быстрое прибытие</strong> — выезжаем за 15-25 минут</li>
    <li><strong>Опытные водители</strong> — профессионалы своего дела</li>
    <li><strong>Современные эвакуаторы</strong> — надежная техника</li>
    <li><strong>Без повреждений</strong> — безопасная эвакуация вашего авто</li>
    <li><strong>Любые расстояния</strong> — по городу и за его пределы</li>
    <li><strong>Работа 24/7</strong> — в любое время дня и ночи</li>
  </ul>
</div>

<div class="service-types">
  <h3>Виды эвакуации</h3>
  <ul>
    <li><strong>Частичная погрузка</strong> — передняя или задняя ось на платформе</li>
    <li><strong>Полная погрузка</strong> — автомобиль полностью на платформе</li>
    <li><strong>Манипулятор</strong> — для тяжелой техники и спецтранспорта</li>
  </ul>
</div>

<div class="service-pricing">
  <h3>Стоимость эвакуатора</h3>
  <p>Цена на услуги эвакуатора в {city_name} зависит от расстояния, типа автомобиля 
  и способа погрузки. Точную стоимость вы узнаете при оформлении заказа.</p>
</div>

<div class="service-faq">
  <h3>Часто задаваемые вопросы</h3>
  <details>
    <summary>Как быстро приедет эвакуатор?</summary>
    <p>В среднем 15-25 минут в зависимости от вашего местоположения и загруженности дорог.</p>
  </details>
  <details>
    <summary>Можно ли ехать в кабине с водителем?</summary>
    <p>Да, вы можете ехать в кабине эвакуатора вместе с водителем.</p>
  </details>
  <details>
    <summary>Эвакуируете ли вы неисправные автомобили?</summary>
    <p>Да, мы эвакуируем автомобили с любыми неисправностями, в том числе не на ходу.</p>
  </details>
</div>
"""
    
    def get_zapravka_template(self, city_name):
        return f"""
<div class="service-intro">
  <h2>Доставка топлива в {city_name}</h2>
  <p>Привезем топливо прямо к вам, если закончился бензин. Быстрая доставка 
  в любую точку {city_name}. Работаем круглосуточно.</p>
</div>

<div class="service-advantages">
  <h3>Преимущества сервиса</h3>
  <ul>
    <li><strong>Быстрая доставка</strong> — приедем за 20-30 минут</li>
    <li><strong>Любое топливо</strong> — АИ-92, АИ-95, АИ-98, дизель</li>
    <li><strong>Безопасность</strong> — сертифицированные канистры</li>
    <li><strong>Любой объем</strong> — от 5 до 20 литров</li>
    <li><strong>Работа 24/7</strong> — в любое время суток</li>
  </ul>
</div>

<div class="service-pricing">
  <h3>Стоимость доставки</h3>
  <p>Цена включает стоимость топлива и доставку. При заказе вы сразу 
  увидите полную стоимость услуги.</p>
</div>
"""
    
    def get_avtovyshka_template(self, city_name):
        return f"""
<div class="service-intro">
  <h2>Аренда автовышки в {city_name}</h2>
  <p>Услуги автовышки для высотных работ в {city_name}. Быстрая подача 
  спецтехники. Опытные операторы.</p>
</div>

<div class="service-advantages">
  <h3>Наши преимущества</h3>
  <ul>
    <li><strong>Быстрая подача</strong> — выезжаем оперативно</li>
    <li><strong>Опытные операторы</strong> — профессионалы своего дела</li>
    <li><strong>Безопасность</strong> — исправная техника</li>
    <li><strong>Разная высота</strong> — от 12 до 28 метров</li>
  </ul>
</div>

<div class="service-pricing">
  <h3>Стоимость услуг</h3>
  <p>Цена зависит от времени аренды и высоты подъема. Уточняйте 
  стоимость при заказе.</p>
</div>
"""
    
    def get_city_template(self, city_name):
        return f"""
<div class="city-intro">
  <h2>Экстренные автоуслуги в {city_name}</h2>
  <p>Платформа 911 предоставляет широкий спектр экстренных автомобильных услуг 
  в {city_name}. Работаем круглосуточно, без выходных.</p>
</div>

<div class="city-services">
  <h3>Доступные услуги</h3>
  <ul>
    <li>Выездной шиномонтаж — замена и ремонт колес на месте</li>
    <li>Эвакуатор — эвакуация легковых и грузовых автомобилей</li>
    <li>Доставка топлива — привезем бензин, если закончился</li>
    <li>Техническая помощь — прикурить, вскрыть, отбуксировать</li>
  </ul>
</div>

<div class="city-how-works">
  <h3>Как заказать услугу</h3>
  <ol>
    <li>Выберите нужную услугу в приложении</li>
    <li>Укажите ваше местоположение</li>
    <li>Подтвердите заказ</li>
    <li>Мастер приедет в течение 20-30 минут</li>
  </ol>
</div>
"""
