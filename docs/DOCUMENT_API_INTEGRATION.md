# Документация API документов для Frontend

## Обзор

API документов предоставляет доступ к юридическим и информационным документам сайта (политика конфиденциальности, оферта, правила использования и т.д.).

**Базовый URL:** `https://api.911.ru/api/website/documents/`

---

## Endpoints

### 1. Получение списка документов

**GET** `/api/website/documents/`

Возвращает список всех **активных** документов.

#### Параметры запроса

| Параметр | Тип | Описание |
|----------|-----|----------|
| `ordering` | string | Сортировка: `-updated_at` (по умолчанию), `updated_at`, `created_at`, `-created_at`, `title`, `-title` |

#### Пример ответа

```json
{
  "count": 3,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "Политика конфиденциальности",
      "slug": "privacy-policy",
      "short_description": "<p>Информация о том, как мы собираем и используем ваши данные.</p>",
      "version": "2.1",
      "updated_at": "2025-12-31T10:00:00Z"
    },
    {
      "id": 2,
      "title": "Пользовательское соглашение",
      "slug": "terms-of-service",
      "short_description": "<p>Условия использования сервиса 911.</p>",
      "version": "1.5",
      "updated_at": "2025-12-15T14:30:00Z"
    },
    {
      "id": 3,
      "title": "Публичная оферта",
      "slug": "public-offer",
      "short_description": "<p>Договор публичной оферты на оказание услуг.</p>",
      "version": "3.0",
      "updated_at": "2025-11-20T09:15:00Z"
    }
  ]
}
```

---

### 2. Получение детальной информации о документе

**GET** `/api/website/documents/{slug}/`

Возвращает полную информацию о документе по его slug.

**Важно:** Если документ не существует или неактивен, возвращается **404 Not Found**.

#### Параметры пути

| Параметр | Тип | Описание |
|----------|-----|----------|
| `slug` | string | URL идентификатор документа (например: `privacy-policy`) |

#### Пример ответа

```json
{
  "id": 1,
  "title": "Политика конфиденциальности",
  "slug": "privacy-policy",
  "short_description": "<p>Информация о том, как мы собираем и используем ваши данные.</p>",
  "full_description": "<h2>1. Общие положения</h2><p>Настоящая политика конфиденциальности...</p><h2>2. Сбор информации</h2><p>Мы собираем следующие типы данных...</p>",
  "version": "2.1",
  "meta_title": "Политика конфиденциальности | 911",
  "meta_description": "Узнайте, как 911 собирает, использует и защищает ваши персональные данные.",
  "meta_keywords": "политика конфиденциальности, персональные данные, защита данных",
  "h1_title": "Политика конфиденциальности",
  "created_at": "2024-01-15T12:00:00Z",
  "updated_at": "2025-12-31T10:00:00Z"
}
```

#### Ответ при ошибке (404)

```json
{
  "detail": "Документ не найден"
}
```

---

## TypeScript интерфейсы

```typescript
// Документ в списке (краткая информация)
interface DocumentListItem {
  id: number;
  title: string;
  slug: string;
  short_description: string; // HTML
  version: string;
  updated_at: string; // ISO 8601
}

// Полная информация о документе
interface DocumentDetail {
  id: number;
  title: string;
  slug: string;
  short_description: string; // HTML
  full_description: string; // HTML
  version: string;
  meta_title: string;
  meta_description: string;
  meta_keywords: string;
  h1_title: string;
  created_at: string; // ISO 8601
  updated_at: string; // ISO 8601
}

// Ответ списка документов
interface DocumentListResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: DocumentListItem[];
}
```

---

## Интеграция с Next.js (App Router)

### API утилита

```typescript
// lib/api.ts
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'https://api.911.ru';

export async function fetchDocuments(): Promise<DocumentListResponse> {
  const res = await fetch(`${API_BASE_URL}/api/website/documents/`, {
    next: { revalidate: 3600 }, // ISR: перегенерация каждый час
  });
  
  if (!res.ok) {
    throw new Error('Failed to fetch documents');
  }
  
  return res.json();
}

export async function fetchDocument(slug: string): Promise<DocumentDetail | null> {
  const res = await fetch(`${API_BASE_URL}/api/website/documents/${slug}/`, {
    next: { revalidate: 3600 },
  });
  
  if (res.status === 404) {
    return null;
  }
  
  if (!res.ok) {
    throw new Error('Failed to fetch document');
  }
  
  return res.json();
}
```

### Страница списка документов

```typescript
// app/documents/page.tsx
import { fetchDocuments } from '@/lib/api';
import Link from 'next/link';

export const metadata = {
  title: 'Документы | 911',
  description: 'Юридические документы и соглашения сервиса 911',
};

export default async function DocumentsPage() {
  const { results: documents } = await fetchDocuments();

  return (
    <main className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-8">Документы</h1>
      
      <div className="grid gap-6">
        {documents.map((doc) => (
          <Link
            key={doc.id}
            href={`/documents/${doc.slug}`}
            className="block p-6 bg-white rounded-lg shadow hover:shadow-md transition-shadow"
          >
            <div className="flex justify-between items-start">
              <div>
                <h2 className="text-xl font-semibold mb-2">{doc.title}</h2>
                <div 
                  className="text-gray-600"
                  dangerouslySetInnerHTML={{ __html: doc.short_description }}
                />
              </div>
              <span className="text-sm text-gray-500">v{doc.version}</span>
            </div>
            <p className="text-sm text-gray-400 mt-4">
              Обновлено: {new Date(doc.updated_at).toLocaleDateString('ru-RU')}
            </p>
          </Link>
        ))}
      </div>
    </main>
  );
}
```

### Страница документа

```typescript
// app/documents/[slug]/page.tsx
import { fetchDocument, fetchDocuments } from '@/lib/api';
import { notFound } from 'next/navigation';
import type { Metadata } from 'next';

interface Props {
  params: { slug: string };
}

// Генерация статических путей для ISR
export async function generateStaticParams() {
  const { results: documents } = await fetchDocuments();
  return documents.map((doc) => ({ slug: doc.slug }));
}

// Динамические метаданные для SEO
export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const doc = await fetchDocument(params.slug);
  
  if (!doc) {
    return { title: 'Документ не найден' };
  }
  
  return {
    title: doc.meta_title,
    description: doc.meta_description,
    keywords: doc.meta_keywords,
  };
}

export default async function DocumentPage({ params }: Props) {
  const doc = await fetchDocument(params.slug);
  
  if (!doc) {
    notFound();
  }
  
  return (
    <main className="container mx-auto px-4 py-8 max-w-4xl">
      <article>
        <header className="mb-8">
          <h1 className="text-3xl font-bold mb-4">{doc.h1_title}</h1>
          <div className="flex gap-4 text-sm text-gray-500">
            <span>Версия: {doc.version}</span>
            <span>
              Обновлено: {new Date(doc.updated_at).toLocaleDateString('ru-RU')}
            </span>
          </div>
        </header>
        
        <div 
          className="prose prose-lg max-w-none"
          dangerouslySetInnerHTML={{ __html: doc.full_description }}
        />
      </article>
    </main>
  );
}
```

---

## Интеграция с Next.js (Pages Router)

### Страница списка документов

```typescript
// pages/documents/index.tsx
import { GetStaticProps } from 'next';
import Link from 'next/link';

interface Props {
  documents: DocumentListItem[];
}

export const getStaticProps: GetStaticProps<Props> = async () => {
  const res = await fetch(`${process.env.API_URL}/api/website/documents/`);
  const data: DocumentListResponse = await res.json();

  return {
    props: {
      documents: data.results,
    },
    revalidate: 3600, // ISR: перегенерация каждый час
  };
};

export default function DocumentsPage({ documents }: Props) {
  return (
    <main className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-8">Документы</h1>
      
      <div className="grid gap-6">
        {documents.map((doc) => (
          <Link key={doc.id} href={`/documents/${doc.slug}`}>
            <a className="block p-6 bg-white rounded-lg shadow hover:shadow-md">
              <h2 className="text-xl font-semibold">{doc.title}</h2>
              <div dangerouslySetInnerHTML={{ __html: doc.short_description }} />
              <p className="text-sm text-gray-500 mt-2">v{doc.version}</p>
            </a>
          </Link>
        ))}
      </div>
    </main>
  );
}
```

### Страница документа

```typescript
// pages/documents/[slug].tsx
import { GetStaticPaths, GetStaticProps } from 'next';
import Head from 'next/head';

interface Props {
  document: DocumentDetail;
}

export const getStaticPaths: GetStaticPaths = async () => {
  const res = await fetch(`${process.env.API_URL}/api/website/documents/`);
  const data: DocumentListResponse = await res.json();

  const paths = data.results.map((doc) => ({
    params: { slug: doc.slug },
  }));

  return { paths, fallback: 'blocking' };
};

export const getStaticProps: GetStaticProps<Props> = async ({ params }) => {
  const slug = params?.slug as string;
  const res = await fetch(`${process.env.API_URL}/api/website/documents/${slug}/`);

  if (res.status === 404) {
    return { notFound: true };
  }

  const document: DocumentDetail = await res.json();

  return {
    props: { document },
    revalidate: 3600,
  };
};

export default function DocumentPage({ document }: Props) {
  return (
    <>
      <Head>
        <title>{document.meta_title}</title>
        <meta name="description" content={document.meta_description} />
        {document.meta_keywords && (
          <meta name="keywords" content={document.meta_keywords} />
        )}
      </Head>
      
      <main className="container mx-auto px-4 py-8 max-w-4xl">
        <article>
          <h1 className="text-3xl font-bold mb-4">{document.h1_title}</h1>
          <div className="text-sm text-gray-500 mb-8">
            Версия: {document.version} | 
            Обновлено: {new Date(document.updated_at).toLocaleDateString('ru-RU')}
          </div>
          
          <div 
            className="prose prose-lg"
            dangerouslySetInnerHTML={{ __html: document.full_description }}
          />
        </article>
      </main>
    </>
  );
}
```

---

## Безопасный рендеринг HTML

Для безопасного рендеринга HTML контента рекомендуется использовать библиотеку `dompurify`:

```bash
npm install dompurify
npm install --save-dev @types/dompurify
```

```typescript
// components/SafeHtml.tsx
'use client';

import DOMPurify from 'dompurify';
import { useEffect, useState } from 'react';

interface Props {
  html: string;
  className?: string;
}

export function SafeHtml({ html, className }: Props) {
  const [sanitizedHtml, setSanitizedHtml] = useState('');

  useEffect(() => {
    setSanitizedHtml(DOMPurify.sanitize(html));
  }, [html]);

  return (
    <div 
      className={className}
      dangerouslySetInnerHTML={{ __html: sanitizedHtml }}
    />
  );
}
```

---

## Обработка ошибок

### HTTP коды ответов

| Код | Описание |
|-----|----------|
| 200 | Успешный запрос |
| 404 | Документ не найден или неактивен |
| 500 | Внутренняя ошибка сервера |

### Пример обработки ошибок

```typescript
async function getDocument(slug: string) {
  try {
    const doc = await fetchDocument(slug);
    
    if (!doc) {
      // Документ не найден - показать 404 страницу
      return { notFound: true };
    }
    
    return { document: doc };
  } catch (error) {
    console.error('Error fetching document:', error);
    // Показать страницу ошибки
    throw error;
  }
}
```

---

## Типичные сценарии использования

### 1. Ссылки в футере

```typescript
// components/Footer.tsx
import Link from 'next/link';

export function Footer() {
  return (
    <footer>
      <nav>
        <Link href="/documents/privacy-policy">Политика конфиденциальности</Link>
        <Link href="/documents/terms-of-service">Пользовательское соглашение</Link>
        <Link href="/documents/public-offer">Публичная оферта</Link>
      </nav>
    </footer>
  );
}
```

### 2. Модальное окно с документом

```typescript
// components/DocumentModal.tsx
'use client';

import { useEffect, useState } from 'react';
import { DocumentDetail } from '@/types';

interface Props {
  slug: string;
  isOpen: boolean;
  onClose: () => void;
}

export function DocumentModal({ slug, isOpen, onClose }: Props) {
  const [doc, setDoc] = useState<DocumentDetail | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isOpen && !doc) {
      setLoading(true);
      fetch(`/api/website/documents/${slug}/`)
        .then((res) => res.json())
        .then((data) => setDoc(data))
        .finally(() => setLoading(false));
    }
  }, [isOpen, slug, doc]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg max-w-2xl max-h-[80vh] overflow-y-auto p-6">
        {loading ? (
          <p>Загрузка...</p>
        ) : doc ? (
          <>
            <h2 className="text-2xl font-bold mb-4">{doc.h1_title}</h2>
            <div dangerouslySetInnerHTML={{ __html: doc.full_description }} />
          </>
        ) : (
          <p>Документ не найден</p>
        )}
        <button onClick={onClose} className="mt-4 px-4 py-2 bg-gray-200 rounded">
          Закрыть
        </button>
      </div>
    </div>
  );
}
```

---

## Примечания

1. **HTML контент**: Поля `short_description` и `full_description` содержат HTML. Используйте `dangerouslySetInnerHTML` или библиотеку для санитизации.

2. **Кэширование**: Рекомендуется использовать ISR (Incremental Static Regeneration) с `revalidate: 3600` (1 час) для оптимальной производительности.

3. **SEO**: Используйте поля `meta_title`, `meta_description` и `meta_keywords` для SEO оптимизации страниц документов.

4. **Версионирование**: Поле `version` позволяет отображать версию документа пользователям.

5. **Неактивные документы**: API возвращает только активные документы. Неактивные документы возвращают 404.

