# 📋 Документация API для создания заявок (Leads)

## Версия: 1.0
**Дата:** 30.12.2025

---

## 📋 Содержание

1. [Обзор](#обзор)
2. [Endpoint для создания заявки](#endpoint-для-создания-заявки)
3. [Типы заявок](#типы-заявок)
4. [Структура запроса](#структура-запроса)
5. [Примеры использования](#примеры-использования)
6. [План интеграции](#план-интеграции)
7. [Обработка ошибок](#обработка-ошибок)
8. [FAQ](#faq)

---

## 🎯 Обзор

API для создания заявок (лидов) с корпоративного сайта. Позволяет отправлять заявки от клиентов с различными типами: заявки по услугам, обратная связь, партнерство.

### Ключевые особенности:

- ✅ **Три типа заявок**: услуга, обратная связь, партнерство
- ✅ **Отслеживание источника**: автоматическое сохранение URL страницы и UTM меток
- ✅ **Гибкая структура**: опциональные поля для разных сценариев
- ✅ **Валидация данных**: проверка телефона и имени на бэкенде

---

## 📡 Endpoint для создания заявки

### URL

```http
POST /api/website/leads/
```

### Базовые URL

```
Production: https://api.911.ru/api/website/leads/
Development: http://localhost:8001/api/website/leads/
```

### Headers

```http
Content-Type: application/json
```

---

## 🏷️ Типы заявок

| Тип | Значение | Описание | Когда использовать |
|-----|----------|----------|---------------------|
| `service` | Заявка по услуге от клиента | Клиент хочет заказать услугу | Формы на страницах услуг, кнопки "Заказать" |
| `feedback` | Заявка с предложениями или обратной связью | Клиент хочет оставить отзыв или предложение | Формы обратной связи, страница контактов |
| `partnership` | Заявка на партнерство | Компания хочет стать партнером | Страница партнерства, форма для партнеров |

**По умолчанию:** `service` (если не указан)

---

## 📦 Структура запроса

### Обязательные поля

| Поле | Тип | Описание | Валидация |
|------|-----|----------|-----------|
| `name` | string | Имя клиента | Минимум 2 символа, максимум 100 |
| `phone` | string | Номер телефона | 10-12 цифр (поддерживает форматы: +7..., 8..., и т.д.) |

### Опциональные поля

| Поле | Тип | Описание | Пример |
|------|-----|----------|--------|
| `email` | string | Email адрес | `ivan@example.com` |
| `city` | integer | ID города | `1` |
| `service` | integer | ID услуги | `2` |
| `message` | string | Сообщение от клиента | `"Нужен шиномонтаж завтра утром"` |
| `lead_type` | string | Тип заявки | `"service"`, `"feedback"`, `"partnership"` |
| `page_url` | string (URL) | **Полный URL страницы** с которой создана заявка | `"https://911.ru/moskva/shinomontazh/?utm_source=google&utm_medium=cpc"` |
| `source_page` | string | Путь страницы (без домена) | `"/moskva/shinomontazh/"` |
| `utm_source` | string | UTM метка: источник | `"google"` |
| `utm_medium` | string | UTM метка: канал | `"cpc"` |
| `utm_campaign` | string | UTM метка: кампания | `"winter2025"` |

### ⚠️ Важно про `page_url`

Поле `page_url` должно содержать **полный URL страницы**, включая:
- Протокол (`https://`)
- Домен (`911.ru`)
- Путь (`/moskva/shinomontazh/`)
- Query параметры (`?utm_source=google&utm_medium=cpc`)

Это позволяет на бэкенде:
- Отслеживать с какой страницы пришла заявка
- Анализировать UTM метки
- Понимать какие фильтры использовал пользователь
- Строить аналитику по источникам трафика

**Как получить на фронте:**

```javascript
// В браузере
const pageUrl = window.location.href; // Полный URL с query параметрами

// В Next.js (SSR)
const pageUrl = `${req.protocol}://${req.get('host')}${req.originalUrl}`;
```

---

## 💡 Примеры использования

### 1. Заявка по услуге (минимальный запрос)

```json
{
  "name": "Иван Иванов",
  "phone": "+79991234567"
}
```

### 2. Заявка по услуге (полный запрос)

```json
{
  "name": "Иван Иванов",
  "phone": "+79991234567",
  "email": "ivan@example.com",
  "city": 1,
  "service": 2,
  "message": "Нужен шиномонтаж завтра утром",
  "lead_type": "service",
  "page_url": "https://911.ru/moskva/shinomontazh/?utm_source=google&utm_medium=cpc&utm_campaign=winter2025",
  "source_page": "/moskva/shinomontazh/",
  "utm_source": "google",
  "utm_medium": "cpc",
  "utm_campaign": "winter2025"
}
```

### 3. Заявка с обратной связью

```json
{
  "name": "Петр Петров",
  "phone": "+79997654321",
  "email": "petr@example.com",
  "message": "Хочу предложить улучшение сервиса. Очень понравился выездной шиномонтаж!",
  "lead_type": "feedback",
  "page_url": "https://911.ru/contacts/",
  "source_page": "/contacts/"
}
```

### 4. Заявка на партнерство

```json
{
  "name": "ООО Компания",
  "phone": "+79998887766",
  "email": "partner@example.com",
  "message": "Интересует сотрудничество. Мы работаем в сфере автосервиса.",
  "lead_type": "partnership",
  "page_url": "https://911.ru/partnership/?ref=partner_site",
  "source_page": "/partnership/"
}
```

---

## 🔧 План интеграции

### Шаг 1: Создать TypeScript типы

```typescript
// types/lead.ts

export type LeadType = 'service' | 'feedback' | 'partnership';

export interface CreateLeadRequest {
  // Обязательные
  name: string;
  phone: string;
  
  // Опциональные
  email?: string;
  city?: number;
  service?: number;
  message?: string;
  lead_type?: LeadType;
  page_url?: string;
  source_page?: string;
  utm_source?: string;
  utm_medium?: string;
  utm_campaign?: string;
}

export interface CreateLeadResponse {
  id: number;
  name: string;
  phone: string;
  email: string | null;
  city: number | null;
  city_title: string | null;
  service: number | null;
  service_title: string | null;
  message: string;
  lead_type: LeadType;
  lead_type_display: string;
  page_url: string | null;
  source_page: string;
  utm_source: string;
  utm_medium: string;
  utm_campaign: string;
  status: 'new' | 'processing' | 'converted' | 'rejected';
  status_display: string;
  created_at: string;
  processed_at: string | null;
}
```

### Шаг 2: Создать API сервис

```typescript
// services/leadService.ts

import axios from 'axios';
import { CreateLeadRequest, CreateLeadResponse } from '@/types/lead';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001';
const API_ENDPOINT = `${API_BASE_URL}/api/website/leads/`;

export const leadService = {
  /**
   * Создать заявку
   */
  async createLead(data: CreateLeadRequest): Promise<CreateLeadResponse> {
    try {
      const response = await axios.post<CreateLeadResponse>(
        API_ENDPOINT,
        data,
        {
          headers: {
            'Content-Type': 'application/json',
          },
        }
      );
      
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        // Обработка ошибок валидации
        if (error.response?.status === 400) {
          throw new Error(
            `Ошибка валидации: ${JSON.stringify(error.response.data)}`
          );
        }
        // Rate limiting
        if (error.response?.status === 429) {
          throw new Error('Превышен лимит запросов. Попробуйте позже.');
        }
      }
      throw error;
    }
  },
  
  /**
   * Получить текущий URL страницы (для page_url)
   */
  getCurrentPageUrl(): string {
    if (typeof window !== 'undefined') {
      return window.location.href;
    }
    return '';
  },
  
  /**
   * Получить путь страницы (для source_page)
   */
  getCurrentPagePath(): string {
    if (typeof window !== 'undefined') {
      return window.location.pathname;
    }
    return '';
  },
  
  /**
   * Получить UTM метки из URL
   */
  getUtmParams(): {
    utm_source?: string;
    utm_medium?: string;
    utm_campaign?: string;
  } {
    if (typeof window === 'undefined') {
      return {};
    }
    
    const params = new URLSearchParams(window.location.search);
    
    return {
      utm_source: params.get('utm_source') || undefined,
      utm_medium: params.get('utm_medium') || undefined,
      utm_campaign: params.get('utm_campaign') || undefined,
    };
  },
};
```

### Шаг 3: Создать хук для отправки заявки

```typescript
// hooks/useCreateLead.ts

import { useState } from 'react';
import { leadService, CreateLeadRequest, CreateLeadResponse } from '@/services/leadService';

export function useCreateLead() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [lead, setLead] = useState<CreateLeadResponse | null>(null);
  
  const createLead = async (data: CreateLeadRequest) => {
    setLoading(true);
    setError(null);
    setSuccess(false);
    
    try {
      // Автоматически добавляем page_url и UTM метки, если не указаны
      const enrichedData: CreateLeadRequest = {
        ...data,
        page_url: data.page_url || leadService.getCurrentPageUrl(),
        source_page: data.source_page || leadService.getCurrentPagePath(),
        ...(data.utm_source ? {} : leadService.getUtmParams()),
      };
      
      const response = await leadService.createLead(enrichedData);
      
      setLead(response);
      setSuccess(true);
      
      return response;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Произошла ошибка';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  };
  
  const reset = () => {
    setError(null);
    setSuccess(false);
    setLead(null);
  };
  
  return {
    createLead,
    loading,
    error,
    success,
    lead,
    reset,
  };
}
```

### Шаг 4: Создать компонент формы заявки

```tsx
// components/LeadForm.tsx

'use client';

import { useState, FormEvent } from 'react';
import { useCreateLead } from '@/hooks/useCreateLead';
import { LeadType } from '@/types/lead';

interface LeadFormProps {
  leadType?: LeadType;
  cityId?: number;
  serviceId?: number;
  onSuccess?: () => void;
}

export function LeadForm({
  leadType = 'service',
  cityId,
  serviceId,
  onSuccess,
}: LeadFormProps) {
  const { createLead, loading, error, success } = useCreateLead();
  
  const [formData, setFormData] = useState({
    name: '',
    phone: '',
    email: '',
    message: '',
  });
  
  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    
    try {
      await createLead({
        ...formData,
        lead_type: leadType,
        city: cityId,
        service: serviceId,
      });
      
      // Очистить форму
      setFormData({
        name: '',
        phone: '',
        email: '',
        message: '',
      });
      
      // Вызвать callback
      if (onSuccess) {
        onSuccess();
      }
    } catch (err) {
      // Ошибка уже обработана в хуке
      console.error('Ошибка создания заявки:', err);
    }
  };
  
  if (success) {
    return (
      <div className="lead-form-success">
        <h3>Спасибо!</h3>
        <p>Ваша заявка успешно отправлена. Мы свяжемся с вами в ближайшее время.</p>
      </div>
    );
  }
  
  return (
    <form onSubmit={handleSubmit} className="lead-form">
      <div className="form-group">
        <label htmlFor="name">Имя *</label>
        <input
          id="name"
          type="text"
          value={formData.name}
          onChange={(e) => setFormData({ ...formData, name: e.target.value })}
          required
          minLength={2}
          maxLength={100}
        />
      </div>
      
      <div className="form-group">
        <label htmlFor="phone">Телефон *</label>
        <input
          id="phone"
          type="tel"
          value={formData.phone}
          onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
          required
          placeholder="+7 (999) 123-45-67"
        />
      </div>
      
      <div className="form-group">
        <label htmlFor="email">Email</label>
        <input
          id="email"
          type="email"
          value={formData.email}
          onChange={(e) => setFormData({ ...formData, email: e.target.value })}
        />
      </div>
      
      <div className="form-group">
        <label htmlFor="message">Сообщение</label>
        <textarea
          id="message"
          value={formData.message}
          onChange={(e) => setFormData({ ...formData, message: e.target.value })}
          rows={4}
        />
      </div>
      
      {error && (
        <div className="form-error">
          {error}
        </div>
      )}
      
      <button type="submit" disabled={loading}>
        {loading ? 'Отправка...' : 'Отправить заявку'}
      </button>
    </form>
  );
}
```

### Шаг 5: Использование на страницах

#### На странице услуги:

```tsx
// pages/[city]/[service]/page.tsx

import { LeadForm } from '@/components/LeadForm';

export default function ServicePage({ params }) {
  const { city, service } = params;
  
  // Получаем данные услуги
  const serviceData = await getServiceData(city, service);
  
  return (
    <div>
      <h1>{serviceData.service.title}</h1>
      
      {/* Форма заявки по услуге */}
      <LeadForm
        leadType="service"
        cityId={serviceData.city.id}
        serviceId={serviceData.service.id}
        onSuccess={() => {
          // Показать модальное окно с благодарностью
          // Или отправить событие в аналитику
        }}
      />
    </div>
  );
}
```

#### На странице контактов:

```tsx
// pages/contacts/page.tsx

import { LeadForm } from '@/components/LeadForm';

export default function ContactsPage() {
  return (
    <div>
      <h1>Контакты</h1>
      
      {/* Форма обратной связи */}
      <LeadForm
        leadType="feedback"
        onSuccess={() => {
          alert('Спасибо за обратную связь!');
        }}
      />
    </div>
  );
}
```

#### На странице партнерства:

```tsx
// pages/partnership/page.tsx

import { LeadForm } from '@/components/LeadForm';

export default function PartnershipPage() {
  return (
    <div>
      <h1>Партнерство</h1>
      
      {/* Форма заявки на партнерство */}
      <LeadForm
        leadType="partnership"
        onSuccess={() => {
          // Показать модальное окно
        }}
      />
    </div>
  );
}
```

---

## ⚠️ Обработка ошибок

### Коды ответов

| Код | Описание | Что делать |
|-----|----------|------------|
| `201` | Заявка успешно создана | Показать сообщение об успехе |
| `400` | Ошибка валидации данных | Показать ошибки валидации пользователю |
| `429` | Превышен лимит запросов | Показать сообщение "Слишком много запросов, попробуйте позже" |
| `500` | Ошибка сервера | Показать общее сообщение об ошибке |

### Пример обработки ошибок валидации

```typescript
try {
  await createLead(data);
} catch (error) {
  if (axios.isAxiosError(error) && error.response?.status === 400) {
    const validationErrors = error.response.data;
    
    // validationErrors может быть объектом с полями:
    // {
    //   "name": ["Имя должно содержать минимум 2 символа"],
    //   "phone": ["Номер телефона должен содержать от 10 до 12 цифр"]
    // }
    
    Object.keys(validationErrors).forEach((field) => {
      // Показать ошибку рядом с полем формы
      setFieldError(field, validationErrors[field][0]);
    });
  }
}
```

---

## ❓ FAQ

### Q: Обязательно ли указывать `page_url`?

**A:** Нет, поле опциональное. Но **рекомендуется** всегда отправлять его, чтобы на бэкенде можно было отслеживать источники заявок. Хук `useCreateLead` автоматически добавляет `page_url`, если он не указан.

### Q: Что если пользователь перешел по ссылке с UTM метками?

**A:** UTM метки автоматически извлекаются из URL и добавляются в запрос (если не указаны явно). Используйте метод `leadService.getUtmParams()`.

### Q: Можно ли отправлять заявку без указания города и услуги?

**A:** Да, поля `city` и `service` опциональные. Например, для заявок типа `feedback` или `partnership` они обычно не нужны.

### Q: Как определить тип заявки на фронте?

**A:** Тип заявки определяется контекстом:
- На странице услуги → `service`
- На странице контактов/обратной связи → `feedback`
- На странице партнерства → `partnership`

### Q: Что делать, если пользователь отправил заявку несколько раз?

**A:** На бэкенде есть rate limiting (5 заявок в час с одного IP). При превышении лимита вернется ошибка `429`. Покажите пользователю сообщение "Слишком много запросов, попробуйте позже".

### Q: Нужно ли валидировать телефон на фронте?

**A:** Рекомендуется добавить базовую валидацию на фронте для лучшего UX, но основная валидация происходит на бэкенде. Бэкенд принимает телефоны в любом формате (с пробелами, скобками, плюсом и т.д.) и проверяет только количество цифр.

---

## 📞 Поддержка

- **Swagger UI**: `http://localhost:8001/api/docs/`
- **ReDoc**: `http://localhost:8001/api/redoc/`
- **OpenAPI Schema**: `http://localhost:8001/api/schema/`

---

## 🔄 История изменений

| Версия | Дата | Изменения |
|--------|------|-----------|
| 1.0 | 30.12.2025 | Первая версия. Добавлены типы заявок и поле page_url |

