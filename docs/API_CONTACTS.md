# API - Контакты (Contacts)

Документация для фронтенда по работе с контактной информацией.

---

## 🎯 Основной эндпоинт

```bash
GET /api/website/contacts/
```

**Описание:** Получить список всех активных контактов компании.

**Особенности:**
- ✅ Возвращает только активные контакты (`is_active=True`)
- ✅ Автоматически отсортированы по `display_order`, затем по `id`
- ✅ Можно фильтровать по типу контакта

---

## 📋 Структура ответа

### Пример запроса

```bash
GET /api/website/contacts/
```

### Пример ответа

```json
{
  "count": 3,
  "results": [
    {
      "id": 1,
      "contact_type": "phone",
      "value": "+7 (999) 123-45-67",
      "label": "Горячая линия",
      "icon_name": "phone",
      "is_active": true,
      "display_order": 1
    },
    {
      "id": 2,
      "contact_type": "whatsapp",
      "value": "https://wa.me/79991234567",
      "label": "WhatsApp",
      "icon_name": "whatsapp",
      "is_active": true,
      "display_order": 2
    },
    {
      "id": 3,
      "contact_type": "telegram",
      "value": "@911_support",
      "label": "Telegram",
      "icon_name": "telegram",
      "is_active": true,
      "display_order": 3
    }
  ]
}
```

---

## 🔍 Фильтрация по типу контакта

Можно получить контакты определенного типа через query-параметр:

```bash
GET /api/website/contacts/?contact_type=phone
GET /api/website/contacts/?contact_type=email
GET /api/website/contacts/?contact_type=whatsapp
```

**Поддерживаемые типы:**
- `phone` - телефоны
- `email` - электронная почта
- `telegram` - Telegram
- `whatsapp` - WhatsApp
- `vk` - ВКонтакте
- `instagram` - Instagram
- `facebook` - Facebook

---

## 📊 Поля данных

| Поле | Тип | Описание | Где использовать |
|------|-----|----------|------------------|
| `id` | number | Уникальный идентификатор | Для ключей в списках (React key) |
| `contact_type` | string | Тип контакта | Для определения иконки и обработки клика |
| `value` | string | **Значение контакта** | ⭐ **Основное поле для отображения** |
| `label` | string | **Текстовая метка** | ⭐ **Подпись/название контакта** |
| `icon_name` | string | Название иконки | Для выбора иконки в UI |
| `is_active` | boolean | Активен ли контакт | Всегда `true` (неактивные не возвращаются) |
| `display_order` | number | Порядок отображения | Для сортировки (меньше = выше) |

---

## 🎨 Где размещать контакты на странице

### 1. **Header (Шапка сайта)**

**Рекомендуемые типы:**
- `phone` - основной телефон
- `email` - email для связи

**Пример использования:**
```javascript
// Получить только телефон для шапки
const headerContacts = contacts.filter(c => c.contact_type === 'phone');
// Использовать: value для ссылки tel:, label для текста
```

**Что выводить:**
- `value` - для атрибута `href="tel:{value}"` или просто текст
- `label` - для отображения под телефоном (опционально)

---

### 2. **Footer (Подвал сайта)**

**Рекомендуемые типы:**
- `phone` - телефоны
- `email` - email
- `whatsapp`, `telegram` - мессенджеры
- `vk`, `instagram`, `facebook` - социальные сети

**Пример использования:**
```javascript
// Получить все контакты для футера
const footerContacts = contacts;
// Группировать по типам или вывести списком
```

**Что выводить:**
- `label` - название контакта (например, "Горячая линия")
- `value` - значение для ссылки или текста
- `icon_name` - для отображения иконки

---

### 3. **Контактная форма / Секция "Свяжитесь с нами"**

**Рекомендуемые типы:**
- Все активные контакты

**Пример использования:**
```javascript
// Получить контакты для блока связи
const contactSection = contacts;
// Отобразить как кнопки/ссылки с иконками
```

**Что выводить:**
- `label` - текст кнопки/ссылки
- `value` - для `href` или `tel:` или `mailto:`
- `icon_name` - иконка рядом с текстом
- `contact_type` - для формирования правильной ссылки

---

### 4. **Всплывающее окно / Модальное окно контактов**

**Рекомендуемые типы:**
- Все активные контакты, сгруппированные по типам

**Пример использования:**
```javascript
// Группировка контактов
const groupedContacts = {
  phones: contacts.filter(c => c.contact_type === 'phone'),
  messengers: contacts.filter(c => ['whatsapp', 'telegram'].includes(c.contact_type)),
  social: contacts.filter(c => ['vk', 'instagram', 'facebook'].includes(c.contact_type)),
  email: contacts.filter(c => c.contact_type === 'email')
};
```

---

## 💡 Примеры формирования ссылок

### Телефон (`contact_type: "phone"`)
```javascript
<a href={`tel:${contact.value.replace(/\s/g, '')}`}>
  {contact.value}
</a>
// Результат: <a href="tel:+79991234567">+7 (999) 123-45-67</a>
```

### Email (`contact_type: "email"`)
```javascript
<a href={`mailto:${contact.value}`}>
  {contact.label || contact.value}
</a>
// Результат: <a href="mailto:support@911.ru">Email поддержки</a>
```

### WhatsApp (`contact_type: "whatsapp"`)
```javascript
<a href={contact.value} target="_blank" rel="noopener noreferrer">
  {contact.label}
</a>
// contact.value уже содержит полную ссылку (например, https://wa.me/79991234567)
```

### Telegram (`contact_type: "telegram"`)
```javascript
<a href={`https://t.me/${contact.value.replace('@', '')}`} target="_blank">
  {contact.label}
</a>
// Если value содержит @, убираем его
```

### Социальные сети (`vk`, `instagram`, `facebook`)
```javascript
<a href={contact.value} target="_blank" rel="noopener noreferrer">
  {contact.label}
</a>
// contact.value содержит полную ссылку на профиль
```

---

## 🎯 Рекомендации по использованию полей

### Основные поля для отображения:

1. **`label`** - всегда показывайте пользователю
   - Это понятное название контакта ("Горячая линия", "WhatsApp", "Email поддержки")

2. **`value`** - используйте для:
   - Формирования ссылок (`href`, `tel:`, `mailto:`)
   - Отображения как текст (если нужен только номер/адрес без label)

3. **`icon_name`** - для выбора иконки
   - Используйте в соответствии с вашей системой иконок
   - Примеры: `phone`, `whatsapp`, `telegram`, `vk`, `instagram`, `email`

4. **`contact_type`** - для:
   - Определения логики обработки клика
   - Группировки контактов
   - Выбора стилей/иконок по типу

5. **`display_order`** - для сортировки
   - Уже отсортированы в ответе API
   - Можно использовать для дополнительной кастомной сортировки

---

## 📱 Пример компонента (React)

```jsx
import { useEffect, useState } from 'react';

function ContactList({ contactType = null }) {
  const [contacts, setContacts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const url = contactType 
      ? `/api/website/contacts/?contact_type=${contactType}`
      : '/api/website/contacts/';
    
    fetch(url)
      .then(res => res.json())
      .then(data => {
        setContacts(data.results);
        setLoading(false);
      });
  }, [contactType]);

  const getLink = (contact) => {
    switch(contact.contact_type) {
      case 'phone':
        return `tel:${contact.value.replace(/\s/g, '')}`;
      case 'email':
        return `mailto:${contact.value}`;
      case 'telegram':
        const telegramValue = contact.value.startsWith('@') 
          ? contact.value.slice(1) 
          : contact.value;
        return `https://t.me/${telegramValue}`;
      default:
        return contact.value; // whatsapp, vk, instagram, facebook уже содержат полные ссылки
    }
  };

  if (loading) return <div>Загрузка...</div>;

  return (
    <div className="contacts">
      {contacts.map(contact => (
        <a
          key={contact.id}
          href={getLink(contact)}
          target={contact.contact_type !== 'phone' && contact.contact_type !== 'email' ? '_blank' : undefined}
          rel={contact.contact_type !== 'phone' && contact.contact_type !== 'email' ? 'noopener noreferrer' : undefined}
          className={`contact contact--${contact.contact_type}`}
        >
          {contact.icon_name && (
            <Icon name={contact.icon_name} />
          )}
          <span className="contact__label">{contact.label}</span>
          {contact.contact_type === 'phone' && (
            <span className="contact__value">{contact.value}</span>
          )}
        </a>
      ))}
    </div>
  );
}

// Использование:
// <ContactList /> - все контакты
// <ContactList contactType="phone" /> - только телефоны
```

---

## 🔄 Получение одного контакта

```bash
GET /api/website/contacts/{id}/
```

**Описание:** Получить детальную информацию об одном контакте.

**Пример:**
```bash
GET /api/website/contacts/1/
```

**Ответ:**
```json
{
  "id": 1,
  "contact_type": "phone",
  "value": "+7 (999) 123-45-67",
  "label": "Горячая линия",
  "icon_name": "phone",
  "is_active": true,
  "display_order": 1
}
```

**Примечание:** Возвращает 404 для неактивных контактов.

---

## ✅ Важные замечания

1. **Всегда используйте `label`** - это понятное название для пользователя
2. **Проверяйте формат `value`** - для разных типов контактов могут быть разные форматы
3. **Используйте `display_order`** - контакты уже отсортированы, но можете использовать для дополнительной логики
4. **Обрабатывайте `contact_type`** - разные типы требуют разной обработки ссылок
5. **Телефоны:** убирайте пробелы и скобки при формировании `tel:` ссылки
6. **Telegram:** если value начинается с `@`, убирайте его при формировании ссылки

---

## 📚 Дополнительная информация

- Контакты автоматически фильтруются по `is_active=True` (неактивные не возвращаются)
- Сортировка по умолчанию: `display_order` (возрастание), затем `id` (возрастание)
- Все контакты доступны только для чтения (GET запросы)

---

**Дата:** 2025-01-XX  
**Статус:** ✅ Актуально  
**Версия API:** v1

