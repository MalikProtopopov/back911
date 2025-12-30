# Обновление HTML калькулятора для подключения к API
## Как переделать вашу форму чтобы она работала с бэкендом

---

## 🔌 ВАРИАНТ 1: Минимальные изменения (Quick Win)

Если вы просто хотите быстро подключить к API, достаточно обновить JavaScript часть.

### ДО (жёсткий код):
```javascript
const BASE_PRICE = 2000;

select.addEventListener('change', calculatePrice);

function calculatePrice() {
    let price = BASE_PRICE;
    // ... расчёты
}
```

### ПОСЛЕ (из API):
```javascript
let PRICING_DATA = null;

// Загружаем данные при загрузке страницы
async function loadPricingData() {
    try {
        const response = await fetch('http://your-backend.com/api/pricing/data');
        PRICING_DATA = await response.json();
        
        // Заполняем селекты на странице
        populateSelects(PRICING_DATA);
    } catch (error) {
        console.error('Failed to load pricing data:', error);
    }
}

// Заполняем список городов
function populateSelects(data) {
    const citySelect = document.getElementById('city');
    data.cities.forEach(city => {
        const option = document.createElement('option');
        option.value = city.id;
        option.textContent = city.name;
        option.dataset.city = city.name;
        citySelect.appendChild(option);
    });
    
    // Аналогично для других селектов...
}

// Вместо локального расчёта, вызываем API
async function calculatePrice() {
    const serviceId = 1; // ID услуги (жёсткий, или сделать выбираемым)
    const cityId = document.getElementById('city').value;
    const vehicleId = document.getElementById('vehicle').value;
    const tireId = document.getElementById('tire').value;
    const fuelId = document.getElementById('fuel').value;
    const zoneId = document.getElementById('zone').value;
    
    const optionIds = Array.from(
        document.querySelectorAll('#optionsGroup input:checked')
    ).map(cb => parseInt(cb.value));
    
    try {
        const response = await fetch('http://your-backend.com/api/pricing/calculate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                service_id: serviceId,
                city_id: parseInt(cityId),
                vehicle_category_id: vehicleId ? parseInt(vehicleId) : null,
                tire_size_id: tireId ? parseInt(tireId) : null,
                fuel_type_id: fuelId ? parseInt(fuelId) : null,
                delivery_zone_id: zoneId ? parseInt(zoneId) : null,
                option_ids: optionIds
            })
        });
        
        const result = await response.json();
        
        // Обновляем DOM с результатами
        document.getElementById('basePrice').textContent = formatPrice(result.base_price);
        document.getElementById('modifiedPrice').textContent = formatPrice(result.service_price);
        document.getElementById('deliveryPrice').textContent = formatPrice(result.delivery_price);
        document.getElementById('totalPrice').textContent = formatPrice(result.total_price);
        
        // Обновляем разбор расчётов
        updateBreakdown(result.breakdown);
        
    } catch (error) {
        console.error('Failed to calculate price:', error);
    }
}

// При загрузке страницы
window.addEventListener('load', loadPricingData);
```

---

## 🔌 ВАРИАНТ 2: Полная реплика HTML с API подключением

Вот полный обновлённый HTML с работающим подключением к API:

```html
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Калькулятор Цены Услуги</title>
    <style>
        /* Все стили остаются прежними */
        :root {
            --color-primary: #32b8c6;
            --color-text: #134252;
            --color-bg: #fcfcf9;
            --color-border: #d4d4d0;
            --color-success: #2180ad;
            --color-warning: #e6a861;
            --radius: 8px;
            --shadow: 0 2px 8px rgba(0,0,0,0.08);
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background-color: var(--color-bg);
            color: var(--color-text);
            padding: 20px;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
        }

        header {
            text-align: center;
            margin-bottom: 40px;
        }

        header h1 {
            font-size: 28px;
            margin-bottom: 8px;
            color: var(--color-text);
        }

        header p {
            color: #626262;
            font-size: 14px;
        }

        .layout {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
        }

        @media (max-width: 768px) {
            .layout {
                grid-template-columns: 1fr;
            }
        }

        .section {
            background: white;
            border-radius: var(--radius);
            border: 1px solid var(--color-border);
            padding: 24px;
            box-shadow: var(--shadow);
        }

        .section h2 {
            font-size: 18px;
            margin-bottom: 20px;
            color: var(--color-text);
            border-bottom: 2px solid var(--color-primary);
            padding-bottom: 12px;
        }

        .form-group {
            margin-bottom: 18px;
        }

        label {
            display: block;
            font-size: 13px;
            font-weight: 500;
            margin-bottom: 6px;
            color: var(--color-text);
        }

        select, input[type="number"] {
            width: 100%;
            padding: 10px 12px;
            border: 1px solid var(--color-border);
            border-radius: 6px;
            font-size: 14px;
            color: var(--color-text);
            background-color: white;
            appearance: none;
            background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%23134252' stroke-width='2'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E");
            background-repeat: no-repeat;
            background-position: right 10px center;
            background-size: 16px;
            padding-right: 36px;
        }

        select:focus, input:focus {
            outline: none;
            border-color: var(--color-primary);
            box-shadow: 0 0 0 3px rgba(50, 184, 198, 0.1);
        }

        .checkbox-group {
            display: flex;
            flex-direction: column;
            gap: 10px;
            max-height: 250px;
            overflow-y: auto;
            padding: 8px;
            border: 1px solid var(--color-border);
            border-radius: 6px;
            background: #f9f9f9;
        }

        .checkbox-item {
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .checkbox-item input {
            width: 18px;
            height: 18px;
            cursor: pointer;
            accent-color: var(--color-primary);
        }

        .checkbox-item label {
            margin: 0;
            font-size: 13px;
            cursor: pointer;
            flex: 1;
        }

        .checkbox-item .price {
            color: #626262;
            font-size: 12px;
            font-weight: 500;
        }

        .result-card {
            background: linear-gradient(135deg, #f5f5f5 0%, #fafafa 100%);
            border: 1px solid var(--color-border);
            border-radius: var(--radius);
            padding: 20px;
            margin-bottom: 16px;
        }

        .result-card h3 {
            font-size: 12px;
            color: #626262;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 6px;
        }

        .result-card .amount {
            font-size: 28px;
            font-weight: 600;
            color: var(--color-text);
        }

        .result-card.total {
            background: linear-gradient(135deg, var(--color-primary) 0%, #1f7681 100%);
            color: white;
        }

        .result-card.total .amount {
            color: white;
            font-size: 36px;
        }

        .result-card.total h3 {
            color: rgba(255, 255, 255, 0.8);
        }

        .breakdown {
            background: white;
            border-radius: var(--radius);
            border: 1px solid var(--color-border);
            padding: 16px;
            margin-top: 20px;
        }

        .breakdown h3 {
            font-size: 14px;
            margin-bottom: 12px;
            color: var(--color-text);
        }

        .breakdown-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 8px 0;
            border-bottom: 1px solid #e9e9e6;
            font-size: 13px;
        }

        .breakdown-item:last-child {
            border-bottom: none;
        }

        .breakdown-item .label {
            display: flex;
            flex-direction: column;
        }

        .breakdown-item .label-title {
            color: var(--color-text);
            font-weight: 500;
        }

        .breakdown-item .value {
            color: #626262;
            font-weight: 600;
            min-width: 80px;
            text-align: right;
        }

        .breakdown-item .value.positive {
            color: #d4a574;
        }

        .breakdown-item .value.negative {
            color: #32b8c6;
        }

        .divider {
            padding: 8px 0;
            border-top: 2px solid var(--color-primary);
            margin: 8px 0;
            font-weight: 600;
            display: flex;
            justify-content: space-between;
        }

        button {
            width: 100%;
            padding: 12px;
            background-color: var(--color-primary);
            color: white;
            border: none;
            border-radius: 6px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            margin-top: 10px;
        }

        button:hover {
            background-color: #1f7681;
            box-shadow: 0 4px 12px rgba(50, 184, 198, 0.2);
        }

        button:active {
            transform: scale(0.98);
        }

        .note {
            background: #fff8e6;
            border-left: 4px solid var(--color-warning);
            padding: 12px;
            border-radius: 4px;
            font-size: 12px;
            color: #666;
            margin-top: 16px;
        }

        .loading {
            display: none;
            text-align: center;
            color: #999;
            padding: 20px;
        }

        .error {
            background: #fee;
            border-left: 4px solid #f00;
            color: #a00;
            padding: 12px;
            border-radius: 4px;
            margin-top: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🚗 Калькулятор Цены Услуги</h1>
            <p>Выездной шиномонтаж — расчёт стоимости в реальном времени</p>
        </header>

        <div class="layout">
            <!-- Левая панель: Параметры -->
            <div>
                <div class="section">
                    <h2>Параметры Услуги</h2>
                    <div class="loading" id="loadingIndicator">Загружаем данные...</div>

                    <div class="form-group">
                        <label for="city">Город</label>
                        <select id="city">
                            <option value="">— Выберите город —</option>
                        </select>
                    </div>

                    <div class="form-group">
                        <label for="vehicle">Категория Техники</label>
                        <select id="vehicle">
                            <option value="">— Выберите категорию —</option>
                        </select>
                    </div>

                    <div class="form-group">
                        <label for="tire">Размер Шины</label>
                        <select id="tire">
                            <option value="">— Выберите размер —</option>
                        </select>
                    </div>

                    <div class="form-group">
                        <label for="fuel">Тип Топлива</label>
                        <select id="fuel">
                            <option value="">— Выберите тип —</option>
                        </select>
                    </div>

                    <div class="form-group">
                        <label for="zone">Зона Доставки</label>
                        <select id="zone">
                            <option value="">— Выберите зону —</option>
                        </select>
                    </div>
                </div>

                <div class="section">
                    <h2>Дополнительные Опции</h2>
                    <div class="checkbox-group" id="optionsGroup">
                        <!-- Будет заполнено через JavaScript -->
                    </div>
                </div>
            </div>

            <!-- Правая панель: Результаты -->
            <div>
                <div class="section">
                    <h2>Результат Расчёта</h2>

                    <div class="result-card">
                        <h3>Базовая Цена Услуги</h3>
                        <div class="amount" id="basePrice">—</div>
                    </div>

                    <div class="result-card">
                        <h3>С Модификаторами</h3>
                        <div class="amount" id="modifiedPrice">—</div>
                    </div>

                    <div class="result-card">
                        <h3>Стоимость Доставки</h3>
                        <div class="amount" id="deliveryPrice">—</div>
                    </div>

                    <div class="result-card total">
                        <h3>Итоговая Цена</h3>
                        <div class="amount" id="totalPrice">—</div>
                    </div>

                    <div class="breakdown">
                        <h3>Разбор Расчёта</h3>
                        <div id="breakdownDetails"></div>
                    </div>

                    <button onclick="resetCalculator()">Сбросить</button>

                    <div class="note">
                        💡 Цены загружаются из базы данных в реальном времени. 
                        Администратор может обновлять цены, и вы сразу это увидите.
                    </div>
                    
                    <div id="errorMessage" class="error" style="display: none;"></div>
                </div>
            </div>
        </div>
    </div>

    <script>
        const API_BASE = 'http://your-backend.com'; // Замените на ваш адрес бэкенда
        const SERVICE_ID = 1; // ID услуги "Выездной шиномонтаж"
        
        let PRICING_DATA = {
            cities: [],
            services: [],
            serviceOptions: {},
            parameters: {
                VEHICLE_CATEGORY: [],
                TIRE_SIZE: [],
                FUEL_TYPE: []
            },
            deliveryZones: {}
        };

        // ============================================================
        // ЗАГРУЗКА ДАННЫХ
        // ============================================================

        async function loadPricingData() {
            try {
                showLoading(true);
                hideError();

                // Загружаем города
                const citiesResponse = await fetch(`${API_BASE}/api/pricing/cities`);
                PRICING_DATA.cities = await citiesResponse.json();

                // Загружаем параметры
                const vehiclesResponse = await fetch(`${API_BASE}/api/pricing/parameters/VEHICLE_CATEGORY`);
                PRICING_DATA.parameters.VEHICLE_CATEGORY = await vehiclesResponse.json();

                const tiresResponse = await fetch(`${API_BASE}/api/pricing/parameters/TIRE_SIZE`);
                PRICING_DATA.parameters.TIRE_SIZE = await tiresResponse.json();

                const fuelsResponse = await fetch(`${API_BASE}/api/pricing/parameters/FUEL_TYPE`);
                PRICING_DATA.parameters.FUEL_TYPE = await fuelsResponse.json();

                // Загружаем опции услуги
                const optionsResponse = await fetch(`${API_BASE}/api/pricing/services/${SERVICE_ID}/options`);
                PRICING_DATA.serviceOptions = await optionsResponse.json();

                // Заполняем селекты
                populateSelects();

                showLoading(false);
            } catch (error) {
                showError('Ошибка при загрузке данных: ' + error.message);
                showLoading(false);
            }
        }

        // ============================================================
        // ЗАПОЛНЕНИЕ СЕЛЕКТОВ
        // ============================================================

        function populateSelects() {
            // Города
            const citySelect = document.getElementById('city');
            citySelect.innerHTML = '<option value="">— Выберите город —</option>';
            PRICING_DATA.cities.forEach(city => {
                const option = document.createElement('option');
                option.value = city.id;
                option.textContent = city.name;
                citySelect.appendChild(option);
            });

            // Категория техники
            const vehicleSelect = document.getElementById('vehicle');
            vehicleSelect.innerHTML = '<option value="">— Выберите категорию —</option>';
            PRICING_DATA.parameters.VEHICLE_CATEGORY.forEach(param => {
                const option = document.createElement('option');
                option.value = param.id;
                const modifier = param.price_modifier >= 0 ? '+' : '';
                option.textContent = `${param.value} ${modifier}${param.price_modifier} ₽`.replace(' 0 ₽', '');
                vehicleSelect.appendChild(option);
            });

            // Размер шины
            const tireSelect = document.getElementById('tire');
            tireSelect.innerHTML = '<option value="">— Выберите размер —</option>';
            PRICING_DATA.parameters.TIRE_SIZE.forEach(param => {
                const option = document.createElement('option');
                option.value = param.id;
                const modifier = param.price_modifier >= 0 ? '+' : '';
                option.textContent = `${param.value} ${modifier}${param.price_modifier} ₽`.replace(' 0 ₽', '');
                tireSelect.appendChild(option);
            });

            // Тип топлива
            const fuelSelect = document.getElementById('fuel');
            fuelSelect.innerHTML = '<option value="">— Выберите тип —</option>';
            PRICING_DATA.parameters.FUEL_TYPE.forEach(param => {
                const option = document.createElement('option');
                option.value = param.id;
                const modifier = param.price_modifier >= 0 ? '+' : '';
                option.textContent = `${param.value} ${modifier}${param.price_modifier} ₽`.replace(' 0 ₽', '');
                fuelSelect.appendChild(option);
            });

            // Опции
            const optionsGroup = document.getElementById('optionsGroup');
            optionsGroup.innerHTML = '';
            PRICING_DATA.serviceOptions.forEach((option, index) => {
                const div = document.createElement('div');
                div.className = 'checkbox-item';
                const modifier = option.price_modifier >= 0 ? '+' : '';
                const modifierText = option.is_percent ? `${modifier}${option.price_modifier}%` : `${modifier}${option.price_modifier} ₽`;
                div.innerHTML = `
                    <input type="checkbox" id="option${index}" value="${option.id}">
                    <label for="option${index}">${option.name}</label>
                    <span class="price">${modifierText}</span>
                `;
                optionsGroup.appendChild(div);

                document.getElementById(`option${index}`).addEventListener('change', calculatePrice);
            });

            // Слушаем изменения
            document.getElementById('city').addEventListener('change', onCityChange);
            document.getElementById('vehicle').addEventListener('change', calculatePrice);
            document.getElementById('tire').addEventListener('change', calculatePrice);
            document.getElementById('fuel').addEventListener('change', calculatePrice);
            document.getElementById('zone').addEventListener('change', calculatePrice);
        }

        // ============================================================
        // ЗАГРУЗКА ЗОН ДОСТАВКИ ПО ГОРОДУ
        // ============================================================

        async function onCityChange() {
            const cityId = document.getElementById('city').value;
            
            if (!cityId) {
                document.getElementById('zone').innerHTML = '<option value="">— Выберите зону —</option>';
                calculatePrice();
                return;
            }

            try {
                const response = await fetch(`${API_BASE}/api/pricing/cities/${cityId}/delivery-zones`);
                const zones = await response.json();

                const zoneSelect = document.getElementById('zone');
                zoneSelect.innerHTML = '<option value="">— Выберите зону —</option>';
                zones.forEach(zone => {
                    const option = document.createElement('option');
                    option.value = zone.id;
                    option.textContent = `${zone.zone_name} (${formatPrice(zone.delivery_price)})`;
                    zoneSelect.appendChild(option);
                });

                calculatePrice();
            } catch (error) {
                showError('Ошибка при загрузке зон доставки');
            }
        }

        // ============================================================
        // РАСЧЁТ ЦЕНЫ (вызов API)
        // ============================================================

        async function calculatePrice() {
            const serviceId = SERVICE_ID;
            const cityId = document.getElementById('city').value;
            const vehicleId = document.getElementById('vehicle').value;
            const tireId = document.getElementById('tire').value;
            const fuelId = document.getElementById('fuel').value;
            const zoneId = document.getElementById('zone').value;

            const optionIds = Array.from(
                document.querySelectorAll('#optionsGroup input:checked')
            ).map(cb => parseInt(cb.value));

            try {
                const response = await fetch(`${API_BASE}/api/pricing/calculate`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        service_id: serviceId,
                        city_id: cityId ? parseInt(cityId) : null,
                        vehicle_category_id: vehicleId ? parseInt(vehicleId) : null,
                        tire_size_id: tireId ? parseInt(tireId) : null,
                        fuel_type_id: fuelId ? parseInt(fuelId) : null,
                        delivery_zone_id: zoneId ? parseInt(zoneId) : null,
                        option_ids: optionIds
                    })
                });

                const result = await response.json();

                if (result.error) {
                    showError(result.error);
                    return;
                }

                // Обновляем результаты
                document.getElementById('basePrice').textContent = formatPrice(result.base_price);
                document.getElementById('modifiedPrice').textContent = formatPrice(result.service_price);
                document.getElementById('deliveryPrice').textContent = formatPrice(result.delivery_price);
                document.getElementById('totalPrice').textContent = formatPrice(result.total_price);

                updateBreakdown(result.breakdown);
                hideError();
            } catch (error) {
                showError('Ошибка при расчёте цены: ' + error.message);
            }
        }

        // ============================================================
        // ОБНОВЛЕНИЕ РАЗБОРА РАСЧЁТОВ
        // ============================================================

        function updateBreakdown(breakdown) {
            const html = breakdown.map(item => {
                let valueClass = 'value';
                if (item.type !== 'base' && item.type !== 'delivery') {
                    valueClass = item.value >= 0 ? 'value positive' : 'value negative';
                }

                return `
                    <div class="breakdown-item">
                        <div class="label">
                            <span class="label-title">${item.label}</span>
                        </div>
                        <div class="${valueClass}">${item.value >= 0 ? '+' : ''}${formatPrice(item.value)}</div>
                    </div>
                `;
            }).join('');

            document.getElementById('breakdownDetails').innerHTML = html;
        }

        // ============================================================
        // УТИЛИТЫ
        // ============================================================

        function formatPrice(value) {
            return Math.round(value).toLocaleString('ru-RU') + ' ₽';
        }

        function resetCalculator() {
            document.getElementById('city').value = '';
            document.getElementById('vehicle').value = '';
            document.getElementById('tire').value = '';
            document.getElementById('fuel').value = '';
            document.getElementById('zone').value = '';
            document.querySelectorAll('#optionsGroup input[type="checkbox"]').forEach(cb => cb.checked = false);
            calculatePrice();
        }

        function showLoading(show) {
            document.getElementById('loadingIndicator').style.display = show ? 'block' : 'none';
        }

        function showError(message) {
            const errorDiv = document.getElementById('errorMessage');
            errorDiv.textContent = message;
            errorDiv.style.display = 'block';
        }

        function hideError() {
            document.getElementById('errorMessage').style.display = 'none';
        }

        // ============================================================
        // ИНИЦИАЛИЗАЦИЯ
        // ============================================================

        window.addEventListener('load', loadPricingData);
    </script>
</body>
</html>
```

---

## 📌 КАК ИСПОЛЬЗОВАТЬ

1. **Замените ссылку на бэкенд:**
   ```javascript
   const API_BASE = 'http://localhost:8000'; // Ваш сервер
   ```

2. **Убедитесь, что FastAPI сервер запущен:**
   ```bash
   python -m pip install fastapi uvicorn sqlalchemy
   python calculator-api-integration-example.py
   ```

3. **Откройте HTML в браузере** - данные будут загружаться с API

---

## 🔐 CORS (для локальной разработки)

Если получаете ошибку CORS, добавьте в Python код:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Для разработки; в продакшене уточните домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 📊 РЕЗУЛЬТАТ

✅ Данные загружаются из БД
✅ Цены обновляются в реальном времени
✅ История изменений сохраняется
✅ Легко добавлять новые города, параметры, опции
✅ Админ может менять цены без кода
