# Логика вывода опций с ценами на странице услуги в городе

## 📋 Обзор

Документ описывает полную логику вывода опций услуг с ценами на странице `/cities/[slug]/services/[serviceSlug]`. Реализация включает группировку опций по категориям техники и отображение в виде аккордеона.

**✅ Важные изменения (2025-12-29):**
- API теперь возвращает **массив цен** (`prices`) для каждой опции вместо одной цены
- Опция может иметь несколько цен для разных категорий техники
- Опция показывается в каждой категории, где у неё есть цена
- Если у цены нет категории техники (`technic_category = null`), она попадает в раздел "Прочие услуги"

---

## 🗂️ Структура файлов

### Основные файлы:

1. **Компонент страницы:**
   - `apps/frontend/src/app/cities/[slug]/services/[serviceSlug]/CityServiceContent.tsx`
   - Основной компонент для отображения услуги в городе

2. **API сервис:**
   - `apps/frontend/src/lib/api/services/cities.service.ts`
   - Определение типов и методы для работы с API

3. **Хук для данных:**
   - `apps/frontend/src/lib/api/hooks/useCities.ts`
   - Хук `useCityService` для загрузки данных

4. **Страница Next.js:**
   - `apps/frontend/src/app/cities/[slug]/services/[serviceSlug]/page.tsx`
   - Server Component обертка

---

## 📊 Структура данных

### Интерфейс опции (`CityServiceOption`)

```typescript
interface CityServiceOption {
  id: number                    // Уникальный ID опции
  title: string                 // Название опции (например, "Балансировка колеса")
  service_id: number            // ID услуги
  service_title: string         // Название услуги
  service_slug: string          // Slug услуги
  is_active: boolean            // Активна ли опция
  prices: Array<{                // Массив цен опции (может быть несколько цен для разных категорий техники)
    amount: string              // Сумма в формате "500.00"
    technic_category: string | null  // Категория техники (например, "Грузовой автомобиль")
  }>                            // Пустой массив если цены не указаны
}
```

**✅ Важно:** 
- Каждая опция имеет **массив цен** (`prices`) - может быть несколько цен для разных категорий техники
- Каждая цена может иметь категорию техники (`technic_category`)
- Если `technic_category` = `null`, цена попадает в раздел "Прочие услуги"
- Если у опции несколько цен с разными категориями, опция будет показана в каждой соответствующей категории

### Интерфейс ответа API (`CityServiceResponse`)

```typescript
interface CityServiceResponse {
  city: {
    id: number
    title: string
    slug: string
    partner_count: number
  }
  service: {
    id: number
    title: string
    slug: string
    icon_url?: string
    options_count: number
  }
  options: CityServiceOption[]  // Массив опций с ценами
  content: { ... } | null       // HTML контент страницы
  seo: { ... } | null           // SEO метаданные
}
```

---

## 🔄 Поток данных

### 1. Загрузка данных

**Хук:** `useCityService(citySlug, serviceSlug)`

**API запрос:**
```
GET /api/website/cities/{city_slug}/services/{service_slug}/
```

**Реализация:**
```typescript
// apps/frontend/src/lib/api/services/cities.service.ts
getServiceByCity: async (citySlug, serviceSlug) => {
  const response = await Service.websiteCitiesServicesRetrieve(citySlug, serviceSlug)
  return response as CityServiceResponse
}
```

**Возвращает:**
- `city` - информация о городе
- `service` - информация об услуге
- `options` - массив опций (каждая с массивом цен для всех категорий техники в данном городе)
- `content` - HTML контент
- `seo` - SEO данные

### 2. Обработка данных

**Хук возвращает:**
```typescript
const {
  city,           // Город
  service,        // Услуга
  options,        // Массив опций
  content,        // Контент
  seo,            // SEO
  isLoading,      // Загрузка
  isError,        // Ошибка
  error           // Объект ошибки
} = useCityService(citySlug, serviceSlug)
```

---

## 🎯 Логика группировки опций

### Функция `groupOptionsByCategory()`

**Расположение:** `CityServiceContent.tsx`, строки 32-49

**Логика:**

```typescript
function groupOptionsByCategory(options: CityServiceOption[]) {
  const grouped: Record<string, Array<{option: CityServiceOption, price: {amount: string, technic_category: string | null}}>> = {}
  const uncategorized: Array<{option: CityServiceOption, price: {amount: string, technic_category: string | null}}> = []

  options.forEach(option => {
    // Если у опции нет цен, пропускаем
    if (!option.prices || option.prices.length === 0) {
      return
    }

    // Обрабатываем каждую цену опции
    option.prices.forEach(price => {
      if (price.technic_category) {
        // Цена с категорией техники
        const category = price.technic_category
      if (!grouped[category]) {
        grouped[category] = []
      }
        grouped[category].push({ option, price })
    } else {
        // Цена без категории - попадает в "Прочие услуги"
        uncategorized.push({ option, price })
    }
    })
  })

  return { grouped, uncategorized }
}
```

**Результат:**
- `grouped` - объект, где ключ = название категории, значение = массив объектов `{option, price}`
- `uncategorized` - массив объектов `{option, price}` без категории

**Пример:**
```typescript
// Входные данные:
options = [
  { 
    id: 1, 
    title: "Балансировка", 
    prices: [
      { amount: "500", technic_category: "Грузовой автомобиль" },
      { amount: "300", technic_category: "Легковой автомобиль" }
    ]
  },
  { 
    id: 2, 
    title: "Шиномонтаж", 
    prices: [
      { amount: "300", technic_category: "Легковой автомобиль" }
    ]
  },
  { 
    id: 3, 
    title: "Ремонт", 
    prices: [
      { amount: "400", technic_category: "Грузовой автомобиль" }
    ]
  },
  { 
    id: 4, 
    title: "Диагностика", 
    prices: [
      { amount: "200", technic_category: null }
    ]
  }
]

// Результат:
{
  grouped: {
    "Грузовой автомобиль": [
      { option: опция1, price: { amount: "500", technic_category: "Грузовой автомобиль" } },
      { option: опция3, price: { amount: "400", technic_category: "Грузовой автомобиль" } }
    ],
    "Легковой автомобиль": [
      { option: опция1, price: { amount: "300", technic_category: "Легковой автомобиль" } },
      { option: опция2, price: { amount: "300", technic_category: "Легковой автомобиль" } }
    ]
  },
  uncategorized: [
    { option: опция4, price: { amount: "200", technic_category: null } }
  ]
}
```

**Использование:**
```typescript
const { grouped, uncategorized } = useMemo(() => {
  return groupOptionsByCategory(options)
}, [options])

const categoryNames = Object.keys(grouped).sort()  // Сортировка категорий
```

---

## 🎨 Компоненты отображения

### 1. Компонент `OptionRow`

**Назначение:** Отображение одной опции в виде строки

**Параметры:**
```typescript
{
  option: CityServiceOption      // Опция для отображения
  showCategory?: boolean         // Показывать ли категорию под названием
}
```

**Структура:**
```
┌─────────────────────────────────────────┐
│ Название опции             500 ₽        │
│ (опционально: категория)                 │
└─────────────────────────────────────────┘
```

**Код:**
```typescript
function OptionRow({ option, price, showCategory = false }) {
  return (
    <div className="option-row-item flex items-center justify-between gap-4 py-3.5 md:py-4 min-h-[56px] hover:bg-slate-50 transition-colors">
      {/* Левая часть: название + подпись */}
      <div className="flex-1 min-w-0">
        <h4 className="text-[15px] md:text-base font-semibold text-[var(--foreground)] leading-tight truncate">
          {option.title}
        </h4>
        {showCategory && price?.technic_category && (
          <p className="text-xs text-[var(--foreground-secondary)]/70 mt-0.5 leading-tight">
            {price.technic_category}
          </p>
        )}
      </div>
      
      {/* Правая часть: цена */}
      {price ? (
        <span className="text-[15px] md:text-base font-semibold text-[var(--color-primary)] flex-shrink-0 tabular-nums">
          {formatPrice(price.amount)}
        </span>
      ) : (
        <Badge variant="secondary" size="sm">По запросу</Badge>
      )}
    </div>
  )
}
```

**Особенности:**
- Hover эффект: `hover:bg-slate-50`
- Форматирование цены через `formatPrice()`
- Если цены нет - показывается бейдж "По запросу"

### 2. Функция форматирования цены `formatPrice()`

**Код:**
```typescript
function formatPrice(amount: string): string {
  const num = parseFloat(amount)
  return new Intl.NumberFormat('ru-RU', {
    style: 'currency',
    currency: 'RUB',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(num)
}
```

**Примеры:**
- `"500.00"` → `"500 ₽"`
- `"1500.50"` → `"1 501 ₽"`

### 3. Компонент `CategorySection`

**Назначение:** Аккордеон-карточка для группы опций одной категории

**Параметры:**
```typescript
{
  title: string                 // Название категории
  options: Array<{               // Массив объектов {option, price} в категории
    option: CityServiceOption
    price: {amount: string, technic_category: string | null}
  }>
  defaultExpanded?: boolean     // Раскрыта ли по умолчанию
}
```

**Структура:**
```
┌─────────────────────────────────────────┐
│ 🚚 Грузовой автомобиль (2 опции)    ▼   │ ← Заголовок (кликабельный)
├─────────────────────────────────────────┤
│ Балансировка колеса           500 ₽     │
│ Ремонт прокола                 400 ₽     │
└─────────────────────────────────────────┘
```

**Код:**
```typescript
function CategorySection({ title, options, defaultExpanded = true }) {
  const [isExpanded, setIsExpanded] = useState(defaultExpanded)

  return (
    <div className="overflow-hidden">
      {/* Заголовок аккордеона */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="category-accordion-button w-full flex items-center justify-between gap-6 pl-12 pr-8 md:pl-16 md:pr-10 py-4 md:py-5 min-h-[64px] md:min-h-[72px] transition-colors duration-150 bg-slate-100 hover:bg-slate-200"
      >
        {/* Левая часть: иконка + название с количеством */}
        <div className="flex items-center gap-4 min-w-0">
          <div className="w-6 h-6 flex items-center justify-center flex-shrink-0">
            <Truck className="w-6 h-6 text-[var(--color-primary)]" />
          </div>
          <span className="font-semibold text-[15px] md:text-base text-[var(--foreground)] truncate">
            {title} ({options.length} {options.length === 1 ? 'опция' : options.length < 5 ? 'опции' : 'опций'})
          </span>
        </div>
        
        {/* Chevron с анимацией */}
        <ChevronDown 
          className={`
            w-6 h-6 text-[var(--foreground-secondary)] flex-shrink-0
            transition-transform duration-200
            ${isExpanded ? 'rotate-180' : 'rotate-0'}
          `} 
        />
      </button>
      
      {/* Тело аккордеона с анимацией */}
      <div 
        className={`
          overflow-hidden transition-all duration-200 ease-out
          ${isExpanded ? 'max-h-[2000px] opacity-100' : 'max-h-0 opacity-0'}
        `}
      >
        <div className="divide-y divide-[var(--border)]/30 bg-white">
          {options.map(({option, price}, index) => (
            <OptionRow 
              key={`${option.id}-${price.technic_category || 'uncategorized'}-${index}`} 
              option={option} 
              price={price}
            />
          ))}
        </div>
      </div>
    </div>
  )
}
```

**Особенности:**
- Управление состоянием через `useState`
- Анимация раскрытия через CSS transitions
- Иконка грузовика для категорий техники
- Склонение слова "опция" в зависимости от количества

---

## 🖼️ Рендеринг на странице

### Структура секции с ценами

**Расположение:** `CityServiceContent.tsx`, строки 249-294

**Код:**
```typescript
{/* Options with prices */}
<div className="pb-8 md:pb-12 pt-8 md:pt-12">
  {/* Заголовок секции */}
  <div className="service-prices-section flex items-baseline gap-3 mb-8">
    <h2 className="service-prices-heading text-2xl md:text-3xl font-bold text-[var(--foreground)]">
      Цены на {service.title.toLowerCase()}
    </h2>
    <Badge variant="secondary" size="sm" className="bg-slate-100 text-slate-600 hidden">
      {options.length} {options.length === 1 ? 'опция' : options.length < 5 ? 'опции' : 'опций'}
    </Badge>
  </div>

  {options.length === 0 ? (
    // Пустое состояние
    <div className="text-center py-12 bg-[var(--background-secondary)] rounded-xl">
      <p className="text-[var(--foreground-secondary)]">
        Цены для данной услуги в этом городе пока не указаны.
      </p>
      <Button asChild className="mt-4">
        <Link href="/contacts">Узнать цены</Link>
      </Button>
    </div>
  ) : (
    <div className="space-y-4">
      {/* Опции, сгруппированные по категориям */}
      {categoryNames.map((category, index) => (
        <CategorySection
          key={category}
          title={category}
          options={grouped[category] ?? []}
          defaultExpanded={index === 0}  // Первая категория открыта
        />
      ))}

      {/* Опции без категории */}
      {uncategorized.length > 0 && (
        <CategorySection
          title="Прочие услуги"
          options={uncategorized}
          defaultExpanded={categoryNames.length === 0}  // Открыта если нет категорий
        />
      )}
    </div>
  )}
</div>
```

**Логика отображения:**

1. **Если опций нет** (`options.length === 0`):
   - Показывается пустое состояние с текстом и кнопкой "Узнать цены"

2. **Если опции есть**:
   - Сначала отображаются категории техники (отсортированные по алфавиту)
   - Первая категория открыта по умолчанию (`defaultExpanded={index === 0}`)
   - Затем отображаются опции без категории в разделе "Прочие услуги"
   - Раздел "Прочие услуги" открыт только если нет категорий

---

## 🎨 Стилизация

### CSS классы и переменные

**Используемые CSS переменные:**
```css
--foreground              /* Основной цвет текста */
--foreground-secondary    /* Вторичный цвет текста */
--color-primary           /* Основной цвет (для цен, иконок) */
--color-success           /* Цвет успеха */
--background-secondary    /* Вторичный фон */
--border                  /* Цвет границ */
```

### Tailwind классы

**Аккордеон:**
- `bg-slate-100` - фон заголовка
- `hover:bg-slate-200` - hover эффект
- `transition-all duration-200` - анимация раскрытия
- `max-h-[2000px]` - максимальная высота при раскрытии
- `opacity-100/opacity-0` - плавное появление/исчезновение

**Строки опций:**
- `hover:bg-slate-50` - hover эффект
- `tabular-nums` - моноширинные цифры для цен
- `truncate` - обрезка длинного текста

---

## ⚙️ Особенности реализации

### 1. Мемоизация группировки

```typescript
const { grouped, uncategorized } = useMemo(() => {
  return groupOptionsByCategory(options)
}, [options])
```

Группировка пересчитывается только при изменении `options`.

### 2. Кастомный аккордеон

Не используется библиотека Radix UI, реализован собственный аккордеон на `useState` и CSS transitions.

### 3. Адаптивность

- Используются responsive классы: `md:py-4`, `md:text-base`
- Минимальные высоты: `min-h-[56px]`, `min-h-[64px]`
- Отступы адаптируются: `pl-12 md:pl-16`

### 4. Склонение слов

```typescript
{options.length === 1 ? 'опция' : options.length < 5 ? 'опции' : 'опций'}
```

Правильное склонение слова "опция" в зависимости от количества.

### 5. Сортировка категорий

```typescript
const categoryNames = Object.keys(grouped).sort()
```

Категории сортируются по алфавиту.

---

## 🔍 Текущие ограничения

### ✅ Реализация: Массив цен на опцию

**Текущая реализация:**
- Каждая опция имеет массив цен (`option.prices`)
- Если у опции есть цены для разных категорий техники, все они возвращаются
- Опция показывается в каждой категории, где у неё есть цена

**Пример:**
```
Опция "Балансировка колеса":
- Грузовой автомобиль: 500 ₽
- Легковой автомобиль: 300 ₽
- Кроссовер: 350 ₽

Вывод: опция показывается в трех категориях с соответствующими ценами
```

**API:**
- `/api/website/cities/{city_slug}/services/{service_slug}/` возвращает опции с массивом цен для данного города
- Каждая цена может иметь категорию техники или быть без категории (попадает в "Прочие услуги")

---

## 📝 Примеры использования

### Пример 1: Опции с категориями

**Входные данные:**
```typescript
options = [
  {
    id: 1,
    title: "Балансировка колеса",
    prices: [
      { amount: "500.00", technic_category: "Грузовой автомобиль" },
      { amount: "300.00", technic_category: "Легковой автомобиль" }
    ]
  },
  {
    id: 2,
    title: "Шиномонтаж R13-R15",
    prices: [
      { amount: "300.00", technic_category: "Легковой автомобиль" }
    ]
  },
  {
    id: 3,
    title: "Ремонт прокола",
    prices: [
      { amount: "400.00", technic_category: "Грузовой автомобиль" }
    ]
  }
]
```

**Результат группировки:**
```typescript
{
  grouped: {
    "Грузовой автомобиль": [
      { option: опция1, price: { amount: "500.00", technic_category: "Грузовой автомобиль" } },
      { option: опция3, price: { amount: "400.00", technic_category: "Грузовой автомобиль" } }
    ],
    "Легковой автомобиль": [
      { option: опция1, price: { amount: "300.00", technic_category: "Легковой автомобиль" } },
      { option: опция2, price: { amount: "300.00", technic_category: "Легковой автомобиль" } }
    ]
  },
  uncategorized: []
}
```

**Отображение:**
```
┌─────────────────────────────────────────┐
│ 🚚 Грузовой автомобиль (2 опции)    ▼   │
├─────────────────────────────────────────┤
│ Балансировка колеса           500 ₽     │
│ Ремонт прокола                 400 ₽     │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│ 🚚 Легковой автомобиль (1 опция)    ▼   │
├─────────────────────────────────────────┤
│ Шиномонтаж R13-R15           300 ₽     │
└─────────────────────────────────────────┘
```

### Пример 2: Опции без категорий

**Входные данные:**
```typescript
options = [
  {
    id: 1,
    title: "Консультация",
    prices: [
      { amount: "0.00", technic_category: null }
    ]
  },
  {
    id: 2,
    title: "Выезд мастера",
    prices: []  // Нет цен
  }
]
```

**Результат:**
```typescript
{
  grouped: {},
  uncategorized: [
    { option: опция1, price: { amount: "0.00", technic_category: null } }
  ]
  // Опция2 не попадает в результат, так как у неё нет цен
}
```

**Отображение:**
```
┌─────────────────────────────────────────┐
│ 🚚 Прочие услуги (2 опции)          ▼   │
├─────────────────────────────────────────┤
│ Консультация                     0 ₽     │
│ Выезд мастера          По запросу        │
└─────────────────────────────────────────┘
```

---

## 🔗 Связанные файлы

- `apps/frontend/src/app/cities/[slug]/services/[serviceSlug]/CityServiceContent.tsx` - Основной компонент
- `apps/frontend/src/lib/api/services/cities.service.ts` - API сервис
- `apps/frontend/src/lib/api/hooks/useCities.ts` - Хук для данных
- `apps/frontend/src/components/ui/` - UI компоненты (Button, Badge, etc.)

---

## 📅 История изменений

- **2025-12-29 01:13** - Первая реализация аккордеона с группировкой по категориям
- Текущая версия: одна цена на опцию, группировка по `technic_category`

---

**Дата создания документа:** 2025-12-29  
**Статус:** ✅ Актуально (коммит 4e7ff58)

