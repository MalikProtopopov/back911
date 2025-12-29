# Дерево метрик проекта 911

Документ содержит полное дерево метрик для партнеров и клиентов, основанное на структуре базы данных.

---

## 📊 МЕТРИКИ ДЛЯ ПАРТНЕРОВ

### 1. БЛОК: Профиль и статус партнера

#### 1.1. Основные характеристики
- **ID партнера** (partner_db.id)
- **Имя и фамилия** (first_name, last_name)
- **Город работы** (city_id → city_db.title)
- **Фото** (photo)
- **Водительские права** (driver_licence)

#### 1.2. Статусы и верификация
- **Статус верификации** (verify)
  - `on_confirmation` - Ожидает подтверждения
  - `confirmed` - Подтвержден
  - `rejected` - Отклонен
  - `blocked` - Заблокирован
- **Дата подтверждения** (date_confirmed)
- **Юридический статус** (legal_status)
  - `legal_entity` - Юридическое лицо
  - `individual` - Физическое лицо
- **Рабочий статус** (is_working)
  - `true` - Работает сейчас
  - `false` - Не работает

#### 1.3. Рейтинг и отзывы
- **Текущий рейтинг** (rating) - числовое значение 0.00-5.00
- **Количество отзывов** (COUNT(review_db WHERE partner_id))
- **Распределение оценок:**
  - Количество 5-звездочных отзывов
  - Количество 4-звездочных отзывов
  - Количество 3-звездочных отзывов
  - Количество 2-звездочных отзывов
  - Количество 1-звездочных отзывов
- **Средний рейтинг за период** (за месяц, квартал, год)
- **Процент положительных отзывов** (4-5 звезд / всего)

**🌐 Для сайта:**
- ✅ Текущий рейтинг
- ✅ Количество отзывов
- ✅ Распределение оценок (визуализация)
- ✅ Процент положительных отзывов

---

### 2. БЛОК: Финансовые метрики

#### 2.1. Балансы
- **Комиссионный баланс** (commission_balance) - текущий остаток
- **Депозитный баланс** (deposit_balance) - текущий остаток
- **Общий баланс** (commission_balance + deposit_balance)
- **История комиссионного баланса** (commission_balance_history - JSON)
- **История депозитного баланса** (deposit_balance_history - JSON)

#### 2.2. Доходы
- **Общий доход** (profit) - накопленный доход за все время
- **Доход за период:**
  - За сегодня
  - За неделю
  - За месяц
  - За квартал
  - За год
- **Средний доход на заказ** (profit / COUNT(orders WHERE status='done'))
- **Доход по услугам** (GROUP BY service_id)
- **Доход по категориям техники** (GROUP BY technic_category_id)

#### 2.3. Комиссии
- **Процент комиссии** (commission_percent)
- **Общая сумма уплаченных комиссий** (SUM(order_db.commission WHERE partner_id))
- **Комиссия за период:**
  - За сегодня
  - За неделю
  - За месяц
  - За квартал
  - За год
- **Средняя комиссия на заказ** (AVG(commission))

#### 2.4. Платежи
- **Количество транзакций пополнения** (COUNT(cloud_payments_transaction_db WHERE balance_type='commission' OR 'deposit'))
- **Сумма пополнений** (SUM(amount WHERE status='success'))
- **Последнее пополнение** (MAX(date_created))

**🌐 Для сайта:**
- ❌ Балансы (конфиденциально)
- ❌ Доходы (конфиденциально)
- ✅ Общий доход (можно показать как "Опыт работы: X заказов")
- ✅ Количество выполненных заказов

---

### 3. БЛОК: Заказы и активность

#### 3.1. Статистика заказов
- **Всего заказов:**
  - Всего принятых (COUNT WHERE partner_id IS NOT NULL)
  - Выполненных (COUNT WHERE status='done')
  - Отмененных (COUNT WHERE status='cancelled')
  - В работе (COUNT WHERE status IN ('on_the_way', 'in_progress', 'on_confirmation'))
- **Процент выполнения** (done / (done + cancelled))
- **Процент отмен** (cancelled / total)

#### 3.2. Заказы по статусам
- **Новые** (status='new' AND partner_id IS NULL) - доступные для принятия
- **В пути** (status='on_the_way')
- **В процессе** (status='in_progress')
- **На подтверждении** (status='on_confirmation')
- **Выполненные** (status='done')
- **Отмененные** (status='cancelled')

#### 3.3. Заказы по услугам
- **Количество заказов по услугам** (GROUP BY service_id)
- **Популярные услуги партнера** (TOP 5 по количеству)
- **Средний чек по услугам** (AVG(total_price) GROUP BY service_id)

#### 3.4. Заказы по категориям техники
- **Количество заказов по категориям** (GROUP BY technic_category_id)
- **Средний чек по категориям** (AVG(total_price) GROUP BY technic_category_id)

#### 3.5. Временные метрики
- **Среднее время выполнения заказа:**
  - От создания до принятия (datetime_created → datetime_updated WHERE status='on_the_way')
  - От принятия до начала работы (status='on_the_way' → 'in_progress')
  - От начала до завершения (status='in_progress' → 'done')
  - Общее время (datetime_created → datetime_updated WHERE status='done')
- **Среднее время отклика** (время от создания заказа до принятия партнером)
- **Самый быстрый отклик** (MIN(время отклика))
- **Самый медленный отклик** (MAX(время отклика))

#### 3.6. Географические метрики
- **Заказы по городам** (GROUP BY city_id) - обычно один город
- **Средний чек по городам** (AVG(total_price) GROUP BY city_id)
- **Рабочие зоны** (через city → working_zone_db)

**🌐 Для сайта:**
- ✅ Количество выполненных заказов
- ✅ Процент выполнения (как "Успешно выполнено X% заказов")
- ✅ Среднее время отклика (как "Средний отклик: X минут")
- ✅ Популярные услуги партнера
- ✅ Опыт работы (количество заказов)

---

### 4. БЛОК: Услуги партнера

#### 4.1. Предоставляемые услуги
- **Количество услуг** (COUNT(partner_service_db WHERE partner_id))
- **Список услуг** (partner_service_db → service_db)
- **Статус верификации услуг:**
  - Подтвержденные (verify_status='confirmed')
  - На подтверждении (verify_status='on_confirmation')
  - Отклоненные (verify_status='rejected')
- **Услуги по категориям техники** (GROUP BY technic_category_id)

#### 4.2. Опции услуг
- **Количество опций** (COUNT(partner_service_option_db))
- **Опции по услугам** (GROUP BY service_id)
- **Популярные опции** (через order_option_db)

#### 4.3. Эффективность услуг
- **Количество заказов по услугам** (COUNT(order_db) GROUP BY service_id)
- **Средний чек по услугам** (AVG(total_price) GROUP BY service_id)
- **Доход по услугам** (SUM(profit) GROUP BY service_id)

**🌐 Для сайта:**
- ✅ Список предоставляемых услуг
- ✅ Количество услуг
- ✅ Опыт по каждой услуге (количество выполненных заказов)

---

### 5. БЛОК: Коммуникация

#### 5.1. Чат
- **Количество чатов** (COUNT(chatroom WHERE order.partner_id))
- **Активные чаты** (COUNT WHERE is_active=true)
- **Количество сообщений** (COUNT(chatmessage WHERE chat_room.order.partner_id))
- **Среднее количество сообщений на заказ**
- **Время ответа в чате** (разница между сообщениями клиента и партнера)

#### 5.2. Уведомления
- **Количество FCM токенов** (COUNT(fcmtoken_db WHERE user_type='partner'))
- **Статус уведомлений** (активен/неактивен)

**🌐 Для сайта:**
- ❌ Детали чата (конфиденциально)
- ✅ "Всегда на связи" (если is_working=true)

---

### 6. БЛОК: Производительность и качество

#### 6.1. Скорость работы
- **Среднее время выполнения заказа** (в минутах/часах)
- **Медианное время выполнения**
- **Процент заказов выполненных в срок** (если есть дедлайны)

#### 6.2. Качество обслуживания
- **Процент положительных отзывов** (4-5 звезд)
- **Процент отрицательных отзывов** (1-2 звезды)
- **Количество жалоб** (через отзывы с низким рейтингом)
- **Тренд рейтинга** (изменение рейтинга во времени)

#### 6.3. Надежность
- **Процент выполненных заказов** (done / total)
- **Процент отмененных заказов** (cancelled / total)
- **Количество повторных клиентов** (COUNT(DISTINCT client_id) WHERE COUNT(order_id) > 1)

**🌐 Для сайта:**
- ✅ Среднее время выполнения
- ✅ Процент положительных отзывов
- ✅ Процент выполненных заказов
- ✅ Количество повторных клиентов (как "X довольных клиентов")

---

## 👥 МЕТРИКИ ДЛЯ КЛИЕНТОВ

### 1. БЛОК: Профиль клиента

#### 1.1. Основные данные
- **ID клиента** (client_db.id)
- **Имя** (first_name)
- **Статус клиента** (client_status)
  - `active` - Активен
  - `blocked` - Заблокирован
- **Телефон** (через users_customuser)

#### 1.2. Автомобили
- **Количество автомобилей** (COUNT(technic_db WHERE client_id))
- **Список автомобилей:**
  - Марка (brand)
  - Модель (car_model)
  - Категория (category_id → technic_category_db)
- **Популярные категории техники** (GROUP BY category_id)

**🌐 Для сайта:**
- ❌ Личные данные (конфиденциально)
- ✅ Общая статистика (анонимизированная)

---

### 2. БЛОК: История заказов

#### 2.1. Общая статистика заказов
- **Всего заказов** (COUNT(order_db WHERE client_id))
- **Выполненных заказов** (COUNT WHERE status='done')
- **Отмененных заказов** (COUNT WHERE status='cancelled')
- **Активных заказов** (COUNT WHERE status IN ('new', 'on_the_way', 'in_progress', 'on_confirmation'))
- **Первый заказ** (MIN(datetime_created))
- **Последний заказ** (MAX(datetime_created))
- **Период активности** (последний заказ - первый заказ)

#### 2.2. Заказы по статусам
- **Новые** (status='new')
- **В пути** (status='on_the_way')
- **В процессе** (status='in_progress')
- **На подтверждении** (status='on_confirmation')
- **Выполненные** (status='done')
- **Отмененные** (status='cancelled')

#### 2.3. Заказы по услугам
- **Количество заказов по услугам** (GROUP BY service_id)
- **Популярные услуги** (TOP 5 по количеству)
- **Средний чек по услугам** (AVG(total_price) GROUP BY service_id)

#### 2.4. Заказы по категориям техники
- **Количество заказов по категориям** (GROUP BY technic_category_id)
- **Средний чек по категориям** (AVG(total_price) GROUP BY technic_category_id)

#### 2.5. Финансовые метрики
- **Общая сумма потраченная** (SUM(total_price WHERE status='done'))
- **Средний чек** (AVG(total_price WHERE status='done'))
- **Минимальный чек** (MIN(total_price))
- **Максимальный чек** (MAX(total_price))
- **Средний чек по услугам** (AVG(total_price) GROUP BY service_id)
- **Траты за период:**
  - За сегодня
  - За неделю
  - За месяц
  - За квартал
  - За год

**🌐 Для сайта:**
- ❌ Личные траты (конфиденциально)
- ✅ Общая статистика платформы (анонимизированная)

---

### 3. БЛОК: Поведение и активность

#### 3.1. Частота заказов
- **Средняя частота заказов** (заказов в месяц)
- **Интервал между заказами** (AVG(разница между datetime_created))
- **Самая активная дата/время** (GROUP BY DATE, HOUR)
- **День недели активности** (GROUP BY DAY_OF_WEEK)

#### 3.2. География заказов
- **Заказы по городам** (GROUP BY city_id)
- **Популярные города** (TOP по количеству заказов)
- **Рабочие зоны** (через city → working_zone_db)

#### 3.3. Предпочтения
- **Любимые услуги** (TOP 3 по количеству)
- **Любимые категории техники** (TOP по количеству)
- **Любимые опции** (через order_option_db)

#### 3.4. Лояльность
- **Повторные заказы** (COUNT WHERE COUNT(order_id) > 1)
- **Количество уникальных партнеров** (COUNT(DISTINCT partner_id))
- **Любимые партнеры** (TOP 3 по количеству заказов)
- **Процент повторных заказов** (повторные / всего)

**🌐 Для сайта:**
- ✅ Популярные услуги (общая статистика)
- ✅ Популярные города (общая статистика)
- ✅ "X довольных клиентов" (COUNT(DISTINCT client_id))

---

### 4. БЛОК: Отзывы и оценки

#### 4.1. Оставленные отзывы
- **Количество отзывов** (COUNT(review_db WHERE client_id))
- **Средняя оценка** (AVG(rating))
- **Распределение оценок:**
  - 5 звезд
  - 4 звезды
  - 3 звезды
  - 2 звезды
  - 1 звезда
- **Отзывы с комментариями** (COUNT WHERE comment IS NOT NULL)
- **Последний отзыв** (MAX(datetime_created))

#### 4.2. Отзывы по партнерам
- **Количество уникальных партнеров с отзывами** (COUNT(DISTINCT partner_id))
- **Средняя оценка по партнерам** (AVG(rating) GROUP BY partner_id)

#### 4.3. Активность отзывов
- **Процент заказов с отзывами** (COUNT(review) / COUNT(orders WHERE status='done'))
- **Тренд отзывов** (количество отзывов по месяцам)

**🌐 Для сайта:**
- ✅ Общее количество отзывов на платформе
- ✅ Средний рейтинг платформы
- ✅ Распределение оценок (визуализация)

---

### 5. БЛОК: Коммуникация

#### 5.1. Чат
- **Количество чатов** (COUNT(chatroom WHERE order.client_id))
- **Активные чаты** (COUNT WHERE is_active=true)
- **Количество сообщений** (COUNT(chatmessage WHERE chat_room.order.client_id))
- **Среднее количество сообщений на заказ**
- **Время ответа партнера** (разница между сообщениями)

#### 5.2. Уведомления
- **Количество FCM токенов** (COUNT(fcmtoken_db WHERE user_type='client'))
- **Статус уведомлений** (активен/неактивен)

**🌐 Для сайта:**
- ❌ Детали чата (конфиденциально)
- ✅ "Быстрая связь с партнером" (как преимущество)

---

### 6. БЛОК: Качество обслуживания

#### 6.1. Удовлетворенность
- **Процент положительных отзывов** (4-5 звезд / всего)
- **Процент отрицательных отзывов** (1-2 звезды / всего)
- **Средний рейтинг полученных услуг** (AVG(rating))

#### 6.2. Проблемы
- **Количество отмененных заказов** (COUNT WHERE status='cancelled'))
- **Причины отмен** (через comment или анализ)
- **Заказы с проблемами** (низкий рейтинг или жалобы)

#### 6.3. Повторное использование
- **Количество повторных заказов** (COUNT WHERE COUNT(order_id) > 1)
- **Количество возвращающихся клиентов** (COUNT(DISTINCT client_id) WHERE COUNT(order_id) > 1)
- **Процент повторных клиентов** (повторные / всего уникальных)

**🌐 Для сайта:**
- ✅ Процент положительных отзывов (общая статистика)
- ✅ Количество довольных клиентов
- ✅ Процент повторных клиентов

---

## 🌐 МЕТРИКИ ДЛЯ КОРПОРАТИВНОГО САЙТА

### Блок 1: Общие метрики платформы

#### 1.1. Масштаб платформы
- ✅ **Общее количество партнеров** (COUNT(partner_db WHERE verify='confirmed'))
- ✅ **Активных партнеров** (COUNT WHERE is_working=true)
- ✅ **Партнеры по городам** (GROUP BY city_id)
- ✅ **Общее количество клиентов** (COUNT(DISTINCT client_db.id))
- ✅ **Активных клиентов** (COUNT WHERE client_status='active')
- ✅ **Общее количество заказов** (COUNT(order_db))
- ✅ **Выполненных заказов** (COUNT WHERE status='done')
- ✅ **Средний рейтинг платформы** (AVG(partner_db.rating))

#### 1.2. География
- ✅ **Количество городов** (COUNT(DISTINCT city_db.id))
- ✅ **Список городов** (city_db.title)
- ✅ **Рабочие зоны** (COUNT(working_zone_db))
- ✅ **Покрытие** (города + зоны на карте)

#### 1.3. Услуги
- ✅ **Количество услуг** (COUNT(service_db))
- ✅ **Список услуг** (service_db.title)
- ✅ **Популярные услуги** (TOP 5 по количеству заказов)
- ✅ **Услуги по городам** (какие услуги доступны в каждом городе)

#### 1.4. Отзывы и рейтинги
- ✅ **Общее количество отзывов** (COUNT(review_db))
- ✅ **Средний рейтинг** (AVG(review_db.rating))
- ✅ **Распределение оценок** (1-5 звезд)
- ✅ **Процент положительных отзывов** (4-5 звезд / всего)
- ✅ **Последние отзывы** (TOP 10 ORDER BY datetime_created DESC)

---

### Блок 2: Метрики по городам (для страниц городов)

#### 2.1. Общая информация о городе
- ✅ **Название города** (city_db.title)
- ✅ **Количество партнеров в городе** (COUNT(partner_db WHERE city_id))
- ✅ **Активных партнеров** (COUNT WHERE is_working=true AND city_id)
- ✅ **Средний рейтинг партнеров в городе** (AVG(rating) WHERE city_id)
- ✅ **Количество выполненных заказов** (COUNT(order_db WHERE city_id AND status='done'))
- ✅ **Рабочие зоны** (working_zone_db WHERE city_id)

#### 2.2. Услуги в городе
- ✅ **Доступные услуги** (через option_price_db → option_db → service_db WHERE city_id)
- ✅ **Популярные услуги** (TOP 5 по количеству заказов WHERE city_id)
- ✅ **Средний чек по услугам** (AVG(total_price) GROUP BY service_id WHERE city_id)

#### 2.3. Цены в городе
- ✅ **Диапазон цен** (MIN(amount), MAX(amount) FROM option_price_db WHERE city_id)
- ✅ **Средние цены по услугам** (AVG(amount) GROUP BY service_id WHERE city_id)
- ✅ **Цены по категориям техники** (AVG(amount) GROUP BY technic_category_id WHERE city_id)

#### 2.4. Активность
- ✅ **Заказы за период** (COUNT WHERE city_id AND datetime_created >= период)
- ✅ **Среднее время отклика** (AVG(время отклика) WHERE city_id)
- ✅ **Процент выполненных заказов** (done / total WHERE city_id)

---

### Блок 3: Метрики по услугам (для страниц услуг)

#### 3.1. Общая информация об услуге
- ✅ **Название услуги** (service_db.title)
- ✅ **Количество партнеров** (COUNT(DISTINCT partner_service_db.partner_id WHERE service_id))
- ✅ **Города присутствия** (DISTINCT city_id через option_price_db)
- ✅ **Количество выполненных заказов** (COUNT(order_db WHERE service_id AND status='done'))
- ✅ **Средний чек** (AVG(total_price WHERE service_id AND status='done'))

#### 3.2. Опции услуги
- ✅ **Список опций** (option_db WHERE service_id)
- ✅ **Количество опций** (COUNT(option_db WHERE service_id))
- ✅ **Популярные опции** (TOP 5 по количеству в order_option_db)

#### 3.3. Цены
- ✅ **Диапазон цен** (MIN(amount), MAX(amount) FROM option_price_db WHERE option.service_id)
- ✅ **Средние цены по городам** (AVG(amount) GROUP BY city_id)
- ✅ **Средние цены по категориям техники** (AVG(amount) GROUP BY technic_category_id)

#### 3.4. Отзывы
- ✅ **Количество отзывов** (COUNT(review_db) через order_db WHERE service_id)
- ✅ **Средний рейтинг** (AVG(rating) через order_db WHERE service_id)
- ✅ **Отзывы по услуге** (TOP 10 ORDER BY datetime_created DESC)

---

### Блок 4: Метрики для страницы "Город + Услуга"

#### 4.1. Комбинированная информация
- ✅ **Услуга в конкретном городе**
- ✅ **Количество партнеров** (COUNT WHERE city_id AND service_id)
- ✅ **Средний рейтинг партнеров** (AVG(rating) WHERE city_id AND service_id)
- ✅ **Количество выполненных заказов** (COUNT WHERE city_id AND service_id AND status='done')

#### 4.2. Детальные цены
- ✅ **Цены по опциям** (option_price_db WHERE city_id AND option.service_id)
- ✅ **Цены по категориям техники** (GROUP BY technic_category_id)
- ✅ **Условия заказа** (order_condition_db WHERE option.service_id)
- ✅ **Цены доставки** (working_zone_db.departure_price WHERE city_id)

#### 4.3. Статистика
- ✅ **Средний чек** (AVG(total_price WHERE city_id AND service_id))
- ✅ **Среднее время выполнения** (AVG(время) WHERE city_id AND service_id)
- ✅ **Среднее время отклика** (AVG(время отклика) WHERE city_id AND service_id)

---

### Блок 5: Социальное доказательство

#### 5.1. Отзывы
- ✅ **Последние отзывы** (TOP 20 ORDER BY datetime_created DESC)
- ✅ **Лучшие отзывы** (TOP 10 ORDER BY rating DESC)
- ✅ **Отзывы с комментариями** (WHERE comment IS NOT NULL)

#### 5.2. Достижения
- ✅ **X довольных клиентов** (COUNT(DISTINCT client_id))
- ✅ **X выполненных заказов** (COUNT WHERE status='done')
- ✅ **X партнеров** (COUNT WHERE verify='confirmed')
- ✅ **Средний рейтинг X.X** (AVG(rating))

#### 5.3. Активность
- ✅ **Заказов за сегодня** (COUNT WHERE DATE(datetime_created) = TODAY)
- ✅ **Заказов за месяц** (COUNT WHERE datetime_created >= начало месяца)
- ✅ **Средний отклик X минут** (AVG(время отклика))

---

## 📈 SQL-запросы для основных метрик

### Для партнеров

```sql
-- Общая статистика партнера
SELECT 
    p.id,
    p.first_name,
    p.last_name,
    p.rating,
    p.is_working,
    COUNT(DISTINCT o.id) as total_orders,
    COUNT(DISTINCT CASE WHEN o.status = 'done' THEN o.id END) as completed_orders,
    SUM(CASE WHEN o.status = 'done' THEN o.total_price ELSE 0 END) as total_revenue,
    AVG(CASE WHEN o.status = 'done' THEN o.total_price END) as avg_order_price,
    COUNT(DISTINCT r.id) as total_reviews,
    AVG(r.rating) as avg_rating
FROM partner_db p
LEFT JOIN order_db o ON o.partner_id = p.id
LEFT JOIN review_db r ON r.partner_id = p.id
WHERE p.id = ?
GROUP BY p.id;
```

### Для клиентов

```sql
-- Общая статистика клиента
SELECT 
    c.id,
    c.first_name,
    COUNT(DISTINCT o.id) as total_orders,
    COUNT(DISTINCT CASE WHEN o.status = 'done' THEN o.id END) as completed_orders,
    SUM(CASE WHEN o.status = 'done' THEN o.total_price ELSE 0 END) as total_spent,
    AVG(CASE WHEN o.status = 'done' THEN o.total_price END) as avg_order_price,
    COUNT(DISTINCT r.id) as total_reviews,
    COUNT(DISTINCT o.partner_id) as unique_partners
FROM client_db c
LEFT JOIN order_db o ON o.client_id = c.id
LEFT JOIN review_db r ON r.client_id = c.id
WHERE c.id = ?
GROUP BY c.id;
```

### Для сайта (общие метрики)

```sql
-- Общие метрики платформы
SELECT 
    COUNT(DISTINCT p.id) as total_partners,
    COUNT(DISTINCT CASE WHEN p.is_working = true THEN p.id END) as active_partners,
    COUNT(DISTINCT c.id) as total_clients,
    COUNT(DISTINCT o.id) as total_orders,
    COUNT(DISTINCT CASE WHEN o.status = 'done' THEN o.id END) as completed_orders,
    AVG(p.rating) as avg_partner_rating,
    AVG(r.rating) as avg_review_rating,
    COUNT(DISTINCT city_db.id) as total_cities
FROM partner_db p
CROSS JOIN client_db c
CROSS JOIN order_db o
LEFT JOIN review_db r ON r.id IS NOT NULL
LEFT JOIN city_db ON city_db.id IS NOT NULL;
```

---

## 🎯 Приоритизация метрик для сайта

### Высокий приоритет (обязательно показать)
1. Общее количество партнеров
2. Общее количество выполненных заказов
3. Средний рейтинг платформы
4. Количество городов
5. Список услуг
6. Количество отзывов
7. Процент положительных отзывов

### Средний приоритет (желательно показать)
1. Активных партнеров
2. Популярные услуги
3. Средний чек
4. Среднее время отклика
5. Распределение оценок
6. Последние отзывы

### Низкий приоритет (можно добавить позже)
1. Детальная статистика по городам
2. Детальная статистика по услугам
3. Тренды и графики
4. Сравнение городов
5. Исторические данные

---

## 📝 Примечания

- **Конфиденциальные данные:** Балансы, доходы, личные данные клиентов и партнеров НЕ должны отображаться на публичном сайте
- **Анонимизация:** При показе отзывов и статистики использовать только публичные данные
- **Производительность:** Для часто запрашиваемых метрик использовать кеширование (Redis)
- **Обновление:** Метрики можно обновлять в реальном времени или с задержкой (например, раз в час)
- **Визуализация:** Использовать графики и диаграммы для лучшего восприятия

