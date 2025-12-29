#!/usr/bin/env python3
"""
Скрипт для расчета бизнес-метрик из дампа БД проекта 911
"""

import re
from collections import defaultdict, Counter
from datetime import datetime
from decimal import Decimal
import json


class DatabaseMetricsCalculator:
    def __init__(self, sql_file):
        self.sql_file = sql_file
        self.data = {
            "cities": {},
            "clients": {},
            "partners": {},
            "orders": [],
            "reviews": [],
            "services": {},
            "partner_services": [],
            "order_options": [],
        }

    def parse_sql_dump(self):
        """Парсит SQL дамп и извлекает данные"""
        print("Парсинг SQL дампа...")

        with open(self.sql_file, "r", encoding="utf-8") as f:
            content = f.read()

        # Парсим города
        self._parse_table(content, "city_db", ["id", "title"], self.data["cities"])

        # Парсим клиентов
        self._parse_table(
            content,
            "client_db",
            ["id", "first_name", "client_status"],
            self.data["clients"],
        )

        # Парсим партнеров
        self._parse_partners(content)

        # Парсим услуги
        self._parse_table(content, "service_db", ["id", "title"], self.data["services"])

        # Парсим заказы
        self._parse_orders(content)

        # Парсим отзывы
        self._parse_reviews(content)

        # Парсим услуги партнеров
        self._parse_partner_services(content)

        print(
            f"Загружено: {len(self.data['cities'])} городов, {len(self.data['clients'])} клиентов, "
            f"{len(self.data['partners'])} партнеров, {len(self.data['orders'])} заказов, "
            f"{len(self.data['reviews'])} отзывов"
        )

    def _parse_table(self, content, table_name, columns, target_dict):
        """Парсит простую таблицу"""
        pattern = rf"COPY public\.{table_name}.*?FROM stdin;(.*?)\\\."
        match = re.search(pattern, content, re.DOTALL)
        if match:
            lines = match.group(1).strip().split("\n")
            for line in lines:
                if line.strip():
                    parts = line.split("\t")
                    if len(parts) >= len(columns):
                        row = {
                            col: parts[i] if i < len(parts) else None
                            for i, col in enumerate(columns)
                        }
                        target_dict[row[columns[0]]] = row

    def _parse_partners(self, content):
        """Парсит партнеров (сложная структура)"""
        pattern = r"COPY public\.partner_db.*?FROM stdin;(.*?)\\\."
        match = re.search(pattern, content, re.DOTALL)
        if match:
            lines = match.group(1).strip().split("\n")
            for line in lines:
                if line.strip():
                    parts = line.split("\t")
                    if len(parts) >= 17:
                        partner = {
                            "id": parts[0],
                            "first_name": parts[1],
                            "last_name": parts[2],
                            "rating": (
                                float(parts[3])
                                if parts[3] and parts[3] != "\\N"
                                else 0.0
                            ),
                            "date_confirmed": parts[4] if parts[4] != "\\N" else None,
                            "legal_status": parts[5],
                            "is_working": parts[6] == "t",
                            "photo": parts[7] if parts[7] != "\\N" else None,
                            "profit": (
                                float(parts[8])
                                if parts[8] and parts[8] != "\\N"
                                else 0.0
                            ),
                            "verify": parts[9],
                            "commission_balance": (
                                float(parts[10])
                                if parts[10] and parts[10] != "\\N"
                                else 0.0
                            ),
                            "deposit_balance": (
                                float(parts[11])
                                if parts[11] and parts[11] != "\\N"
                                else 0.0
                            ),
                            "city_id": parts[14] if parts[14] != "\\N" else None,
                            "commission_percent": (
                                float(parts[16])
                                if parts[16] and parts[16] != "\\N"
                                else 0.0
                            ),
                        }
                        self.data["partners"][partner["id"]] = partner

    def _parse_orders(self, content):
        """Парсит заказы"""
        pattern = r"COPY public\.order_db.*?FROM stdin;(.*?)\\\."
        match = re.search(pattern, content, re.DOTALL)
        if match:
            lines = match.group(1).strip().split("\n")
            for line in lines:
                if line.strip():
                    parts = line.split("\t")
                    if len(parts) >= 18:
                        try:
                            order = {
                                "id": parts[0],
                                "total_price": (
                                    float(parts[3])
                                    if parts[3] and parts[3] != "\\N"
                                    else 0.0
                                ),
                                "options_price": (
                                    float(parts[4])
                                    if parts[4] and parts[4] != "\\N"
                                    else 0.0
                                ),
                                "delivery_price": (
                                    float(parts[5])
                                    if parts[5] and parts[5] != "\\N"
                                    else 0.0
                                ),
                                "status": parts[6],
                                "datetime_created": (
                                    parts[7] if parts[7] != "\\N" else None
                                ),
                                "datetime_updated": (
                                    parts[8] if parts[8] != "\\N" else None
                                ),
                                "commission": (
                                    float(parts[12])
                                    if parts[12] and parts[12] != "\\N"
                                    else 0.0
                                ),
                                "city_id": parts[13] if parts[13] != "\\N" else None,
                                "client_id": parts[14] if parts[14] != "\\N" else None,
                                "partner_id": parts[15] if parts[15] != "\\N" else None,
                                "service_id": parts[16] if parts[16] != "\\N" else None,
                                "technic_category_id": (
                                    parts[17] if parts[17] != "\\N" else None
                                ),
                            }
                            self.data["orders"].append(order)
                        except (ValueError, IndexError) as e:
                            continue

    def _parse_reviews(self, content):
        """Парсит отзывы"""
        pattern = r"COPY public\.review_db.*?FROM stdin;(.*?)\\\."
        match = re.search(pattern, content, re.DOTALL)
        if match:
            lines = match.group(1).strip().split("\n")
            for line in lines:
                if line.strip():
                    parts = line.split("\t")
                    if len(parts) >= 6:
                        try:
                            review = {
                                "id": parts[0],
                                "comment": parts[1] if parts[1] != "\\N" else None,
                                "rating": (
                                    int(parts[2])
                                    if parts[2] and parts[2] != "\\N"
                                    else 0
                                ),
                                "datetime_created": (
                                    parts[3] if parts[3] != "\\N" else None
                                ),
                                "client_id": parts[4] if parts[4] != "\\N" else None,
                                "partner_id": parts[5] if parts[5] != "\\N" else None,
                            }
                            self.data["reviews"].append(review)
                        except (ValueError, IndexError) as e:
                            continue

    def _parse_partner_services(self, content):
        """Парсит услуги партнеров"""
        pattern = r"COPY public\.partner_service_db.*?FROM stdin;(.*?)\\\."
        match = re.search(pattern, content, re.DOTALL)
        if match:
            lines = match.group(1).strip().split("\n")
            for line in lines:
                if line.strip():
                    parts = line.split("\t")
                    if len(parts) >= 5:
                        ps = {
                            "id": parts[0],
                            "verify_status": parts[1],
                            "partner_id": parts[2],
                            "service_id": parts[3],
                            "technic_category_id": (
                                parts[4] if parts[4] != "\\N" else None
                            ),
                        }
                        self.data["partner_services"].append(ps)

    def calculate_metrics(self):
        """Рассчитывает все метрики"""
        print("\n" + "=" * 80)
        print("РАСЧЕТ БИЗНЕС-МЕТРИК")
        print("=" * 80)

        metrics = {}

        # Общие метрики платформы
        metrics["platform"] = self._calculate_platform_metrics()

        # Метрики партнеров
        metrics["partners"] = self._calculate_partner_metrics()

        # Метрики клиентов
        metrics["clients"] = self._calculate_client_metrics()

        # Метрики заказов
        metrics["orders"] = self._calculate_order_metrics()

        # Метрики по городам
        metrics["cities"] = self._calculate_city_metrics()

        # Метрики по услугам
        metrics["services"] = self._calculate_service_metrics()

        return metrics

    def _calculate_platform_metrics(self):
        """Общие метрики платформы"""
        print("\n📊 Общие метрики платформы:")

        confirmed_partners = [
            p for p in self.data["partners"].values() if p["verify"] == "confirmed"
        ]
        active_partners = [p for p in confirmed_partners if p["is_working"]]
        active_clients = [
            c
            for c in self.data["clients"].values()
            if c.get("client_status") == "active"
        ]
        completed_orders = [o for o in self.data["orders"] if o["status"] == "done"]

        avg_rating = (
            sum(p["rating"] for p in confirmed_partners) / len(confirmed_partners)
            if confirmed_partners
            else 0
        )
        avg_review_rating = (
            sum(r["rating"] for r in self.data["reviews"]) / len(self.data["reviews"])
            if self.data["reviews"]
            else 0
        )

        total_revenue = sum(o["total_price"] for o in completed_orders)
        avg_order_price = (
            total_revenue / len(completed_orders) if completed_orders else 0
        )

        positive_reviews = [r for r in self.data["reviews"] if r["rating"] >= 4]
        positive_review_percent = (
            (len(positive_reviews) / len(self.data["reviews"]) * 100)
            if self.data["reviews"]
            else 0
        )

        metrics = {
            "total_cities": len(self.data["cities"]),
            "total_partners": len(confirmed_partners),
            "active_partners": len(active_partners),
            "total_clients": len(active_clients),
            "total_orders": len(self.data["orders"]),
            "completed_orders": len(completed_orders),
            "total_reviews": len(self.data["reviews"]),
            "avg_partner_rating": round(avg_rating, 2),
            "avg_review_rating": round(avg_review_rating, 2),
            "total_revenue": round(total_revenue, 2),
            "avg_order_price": round(avg_order_price, 2),
            "positive_review_percent": round(positive_review_percent, 1),
            "total_services": len(self.data["services"]),
        }

        for key, value in metrics.items():
            print(f"  {key}: {value}")

        return metrics

    def _calculate_partner_metrics(self):
        """Метрики партнеров"""
        print("\n👥 Метрики партнеров:")

        confirmed_partners = [
            p for p in self.data["partners"].values() if p["verify"] == "confirmed"
        ]

        # Статистика по рейтингам
        ratings = [p["rating"] for p in confirmed_partners]
        avg_rating = sum(ratings) / len(ratings) if ratings else 0

        # Партнеры по городам
        partners_by_city = defaultdict(int)
        for p in confirmed_partners:
            if p["city_id"]:
                city_name = (
                    self.data["cities"].get(p["city_id"], {}).get("title", "Unknown")
                )
                partners_by_city[city_name] += 1

        # Топ партнеры по доходу
        partner_profits = {p["id"]: p["profit"] for p in confirmed_partners}
        top_partners_by_profit = sorted(
            partner_profits.items(), key=lambda x: x[1], reverse=True
        )[:10]

        # Партнеры по статусу работы
        working_partners = len([p for p in confirmed_partners if p["is_working"]])

        # Заказы по партнерам
        orders_by_partner = defaultdict(int)
        completed_orders_by_partner = defaultdict(int)
        for o in self.data["orders"]:
            if o["partner_id"]:
                orders_by_partner[o["partner_id"]] += 1
                if o["status"] == "done":
                    completed_orders_by_partner[o["partner_id"]] += 1

        metrics = {
            "total_confirmed": len(confirmed_partners),
            "active_working": working_partners,
            "avg_rating": round(avg_rating, 2),
            "min_rating": round(min(ratings), 2) if ratings else 0,
            "max_rating": round(max(ratings), 2) if ratings else 0,
            "partners_by_city": dict(
                sorted(partners_by_city.items(), key=lambda x: x[1], reverse=True)[:10]
            ),
            "top_partners_by_profit": [
                (pid, round(profit, 2)) for pid, profit in top_partners_by_profit
            ],
            "avg_orders_per_partner": (
                round(len(orders_by_partner) / len(confirmed_partners), 1)
                if confirmed_partners
                else 0
            ),
        }

        print(f"  Всего подтвержденных партнеров: {metrics['total_confirmed']}")
        print(f"  Активных сейчас: {metrics['active_working']}")
        print(f"  Средний рейтинг: {metrics['avg_rating']}")
        print(
            f"  Топ-5 городов по партнерам: {list(metrics['partners_by_city'].items())[:5]}"
        )

        return metrics

    def _calculate_client_metrics(self):
        """Метрики клиентов"""
        print("\n👤 Метрики клиентов:")

        active_clients = [
            c
            for c in self.data["clients"].values()
            if c.get("client_status") == "active"
        ]

        # Заказы по клиентам
        orders_by_client = defaultdict(int)
        completed_orders_by_client = defaultdict(int)
        revenue_by_client = defaultdict(float)

        for o in self.data["orders"]:
            if o["client_id"]:
                orders_by_client[o["client_id"]] += 1
                if o["status"] == "done":
                    completed_orders_by_client[o["client_id"]] += 1
                    revenue_by_client[o["client_id"]] += o["total_price"]

        # Повторные клиенты
        repeat_clients = [cid for cid, count in orders_by_client.items() if count > 1]

        # Топ клиенты по заказам
        top_clients = sorted(
            orders_by_client.items(), key=lambda x: x[1], reverse=True
        )[:10]

        metrics = {
            "total_active": len(active_clients),
            "clients_with_orders": len(orders_by_client),
            "repeat_clients": len(repeat_clients),
            "repeat_client_percent": (
                round(len(repeat_clients) / len(orders_by_client) * 100, 1)
                if orders_by_client
                else 0
            ),
            "avg_orders_per_client": (
                round(sum(orders_by_client.values()) / len(orders_by_client), 1)
                if orders_by_client
                else 0
            ),
            "top_clients": [(cid, count) for cid, count in top_clients],
        }

        print(f"  Всего активных клиентов: {metrics['total_active']}")
        print(f"  Клиентов с заказами: {metrics['clients_with_orders']}")
        print(
            f"  Повторных клиентов: {metrics['repeat_clients']} ({metrics['repeat_client_percent']}%)"
        )
        print(f"  Среднее заказов на клиента: {metrics['avg_orders_per_client']}")

        return metrics

    def _calculate_order_metrics(self):
        """Метрики заказов"""
        print("\n📦 Метрики заказов:")

        # Статусы заказов
        status_counts = Counter(o["status"] for o in self.data["orders"])

        completed_orders = [o for o in self.data["orders"] if o["status"] == "done"]
        cancelled_orders = [
            o for o in self.data["orders"] if o["status"] == "cancelled"
        ]

        # Финансовые метрики
        total_revenue = sum(o["total_price"] for o in completed_orders)
        total_commission = sum(o["commission"] for o in completed_orders)
        avg_order_price = (
            total_revenue / len(completed_orders) if completed_orders else 0
        )

        # Заказы по услугам
        orders_by_service = defaultdict(int)
        revenue_by_service = defaultdict(float)
        for o in completed_orders:
            if o["service_id"]:
                service_name = (
                    self.data["services"]
                    .get(o["service_id"], {})
                    .get("title", "Unknown")
                )
                orders_by_service[service_name] += 1
                revenue_by_service[service_name] += o["total_price"]

        # Заказы по городам
        orders_by_city = defaultdict(int)
        revenue_by_city = defaultdict(float)
        for o in completed_orders:
            if o["city_id"]:
                city_name = (
                    self.data["cities"].get(o["city_id"], {}).get("title", "Unknown")
                )
                orders_by_city[city_name] += 1
                revenue_by_city[city_name] += o["total_price"]

        # Конверсия
        completion_rate = (
            (len(completed_orders) / len(self.data["orders"]) * 100)
            if self.data["orders"]
            else 0
        )
        cancellation_rate = (
            (len(cancelled_orders) / len(self.data["orders"]) * 100)
            if self.data["orders"]
            else 0
        )

        metrics = {
            "total": len(self.data["orders"]),
            "status_distribution": dict(status_counts),
            "completed": len(completed_orders),
            "cancelled": len(cancelled_orders),
            "completion_rate": round(completion_rate, 1),
            "cancellation_rate": round(cancellation_rate, 1),
            "total_revenue": round(total_revenue, 2),
            "total_commission": round(total_commission, 2),
            "avg_order_price": round(avg_order_price, 2),
            "orders_by_service": dict(
                sorted(orders_by_service.items(), key=lambda x: x[1], reverse=True)
            ),
            "revenue_by_service": {
                k: round(v, 2)
                for k, v in sorted(
                    revenue_by_service.items(), key=lambda x: x[1], reverse=True
                )
            },
            "top_cities_by_orders": dict(
                sorted(orders_by_city.items(), key=lambda x: x[1], reverse=True)[:10]
            ),
            "top_cities_by_revenue": {
                k: round(v, 2)
                for k, v in sorted(
                    revenue_by_city.items(), key=lambda x: x[1], reverse=True
                )[:10]
            },
        }

        print(f"  Всего заказов: {metrics['total']}")
        print(f"  Выполнено: {metrics['completed']} ({metrics['completion_rate']}%)")
        print(f"  Отменено: {metrics['cancelled']} ({metrics['cancellation_rate']}%)")
        print(f"  Общий оборот: {metrics['total_revenue']} руб.")
        print(f"  Средний чек: {metrics['avg_order_price']} руб.")
        print(f"  Заказы по услугам: {metrics['orders_by_service']}")

        return metrics

    def _calculate_city_metrics(self):
        """Метрики по городам"""
        print("\n🏙️ Метрики по городам:")

        city_metrics = {}

        for city_id, city in self.data["cities"].items():
            city_name = city.get("title", "Unknown")

            # Партнеры в городе
            partners_in_city = [
                p
                for p in self.data["partners"].values()
                if p["city_id"] == city_id and p["verify"] == "confirmed"
            ]

            # Заказы в городе
            orders_in_city = [o for o in self.data["orders"] if o["city_id"] == city_id]
            completed_orders = [o for o in orders_in_city if o["status"] == "done"]

            # Отзывы по партнерам города
            partner_ids = [p["id"] for p in partners_in_city]
            reviews_in_city = [
                r for r in self.data["reviews"] if r["partner_id"] in partner_ids
            ]

            if partners_in_city or orders_in_city:
                avg_rating = (
                    sum(p["rating"] for p in partners_in_city) / len(partners_in_city)
                    if partners_in_city
                    else 0
                )
                total_revenue = sum(o["total_price"] for o in completed_orders)

                city_metrics[city_name] = {
                    "partners": len(partners_in_city),
                    "active_partners": len(
                        [p for p in partners_in_city if p["is_working"]]
                    ),
                    "orders": len(orders_in_city),
                    "completed_orders": len(completed_orders),
                    "revenue": round(total_revenue, 2),
                    "avg_rating": round(avg_rating, 2),
                    "reviews": len(reviews_in_city),
                }

        # Топ города
        top_cities_by_orders = sorted(
            city_metrics.items(), key=lambda x: x[1]["orders"], reverse=True
        )[:10]
        top_cities_by_revenue = sorted(
            city_metrics.items(), key=lambda x: x[1]["revenue"], reverse=True
        )[:10]

        print(f"  Городов с активностью: {len(city_metrics)}")
        print(f"  Топ-5 по заказам: {[c[0] for c in top_cities_by_orders[:5]]}")

        return {
            "cities": city_metrics,
            "top_by_orders": {c[0]: c[1] for c in top_cities_by_orders},
            "top_by_revenue": {c[0]: c[1] for c in top_cities_by_revenue},
        }

    def _calculate_service_metrics(self):
        """Метрики по услугам"""
        print("\n🔧 Метрики по услугам:")

        service_metrics = {}

        for service_id, service in self.data["services"].items():
            service_name = service.get("title", "Unknown")

            # Заказы по услуге
            orders_by_service = [
                o for o in self.data["orders"] if o["service_id"] == service_id
            ]
            completed_orders = [o for o in orders_by_service if o["status"] == "done"]

            # Партнеры, предоставляющие услугу
            partners_by_service = [
                ps
                for ps in self.data["partner_services"]
                if ps["service_id"] == service_id and ps["verify_status"] == "confirmed"
            ]

            if orders_by_service:
                total_revenue = sum(o["total_price"] for o in completed_orders)
                avg_price = (
                    total_revenue / len(completed_orders) if completed_orders else 0
                )

                service_metrics[service_name] = {
                    "orders": len(orders_by_service),
                    "completed_orders": len(completed_orders),
                    "revenue": round(total_revenue, 2),
                    "avg_price": round(avg_price, 2),
                    "partners": len(
                        set(ps["partner_id"] for ps in partners_by_service)
                    ),
                }

        print(f"  Услуг: {len(service_metrics)}")
        for service, metrics in service_metrics.items():
            print(
                f"  {service}: {metrics['orders']} заказов, {metrics['revenue']} руб."
            )

        return service_metrics

    def generate_report(self, metrics):
        """Генерирует отчет"""
        report = {"generated_at": datetime.now().isoformat(), "metrics": metrics}

        # Сохраняем в JSON
        with open("business_metrics_report.json", "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        # Генерируем текстовый отчет
        self._generate_text_report(metrics)

        print("\n" + "=" * 80)
        print(
            "✅ Отчет сохранен в business_metrics_report.json и business_metrics_report.txt"
        )
        print("=" * 80)

    def _generate_text_report(self, metrics):
        """Генерирует текстовый отчет"""
        with open("business_metrics_report.txt", "w", encoding="utf-8") as f:
            f.write("=" * 80 + "\n")
            f.write("БИЗНЕС-МЕТРИКИ ПРОЕКТА 911\n")
            f.write(f"Сгенерировано: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 80 + "\n\n")

            # Общие метрики
            f.write("📊 ОБЩИЕ МЕТРИКИ ПЛАТФОРМЫ\n")
            f.write("-" * 80 + "\n")
            platform = metrics["platform"]
            f.write(f"Городов: {platform['total_cities']}\n")
            f.write(
                f"Партнеров: {platform['total_partners']} (активных: {platform['active_partners']})\n"
            )
            f.write(f"Клиентов: {platform['total_clients']}\n")
            f.write(
                f"Заказов: {platform['total_orders']} (выполнено: {platform['completed_orders']})\n"
            )
            f.write(f"Отзывов: {platform['total_reviews']}\n")
            f.write(f"Средний рейтинг партнеров: {platform['avg_partner_rating']}\n")
            f.write(f"Средний рейтинг отзывов: {platform['avg_review_rating']}\n")
            f.write(f"Общий оборот: {platform['total_revenue']} руб.\n")
            f.write(f"Средний чек: {platform['avg_order_price']} руб.\n")
            f.write(
                f"Процент положительных отзывов: {platform['positive_review_percent']}%\n\n"
            )

            # Метрики заказов
            f.write("📦 МЕТРИКИ ЗАКАЗОВ\n")
            f.write("-" * 80 + "\n")
            orders = metrics["orders"]
            f.write(f"Всего заказов: {orders['total']}\n")
            f.write(
                f"Выполнено: {orders['completed']} ({orders['completion_rate']}%)\n"
            )
            f.write(
                f"Отменено: {orders['cancelled']} ({orders['cancellation_rate']}%)\n"
            )
            f.write(f"Общий оборот: {orders['total_revenue']} руб.\n")
            f.write(f"Общая комиссия: {orders['total_commission']} руб.\n")
            f.write(f"Средний чек: {orders['avg_order_price']} руб.\n\n")

            f.write("Заказы по услугам:\n")
            for service, count in orders["orders_by_service"].items():
                revenue = orders["revenue_by_service"].get(service, 0)
                f.write(f"  {service}: {count} заказов, {revenue} руб.\n")
            f.write("\n")

            f.write("Топ-10 городов по заказам:\n")
            for city, count in list(orders["top_cities_by_orders"].items())[:10]:
                revenue = orders["top_cities_by_revenue"].get(city, 0)
                f.write(f"  {city}: {count} заказов, {revenue} руб.\n")
            f.write("\n")

            # Метрики партнеров
            f.write("👥 МЕТРИКИ ПАРТНЕРОВ\n")
            f.write("-" * 80 + "\n")
            partners = metrics["partners"]
            f.write(f"Подтвержденных партнеров: {partners['total_confirmed']}\n")
            f.write(f"Активных сейчас: {partners['active_working']}\n")
            f.write(f"Средний рейтинг: {partners['avg_rating']}\n")
            f.write(
                f"Среднее заказов на партнера: {partners['avg_orders_per_partner']}\n\n"
            )

            f.write("Топ-5 городов по партнерам:\n")
            for city, count in list(partners["partners_by_city"].items())[:5]:
                f.write(f"  {city}: {count} партнеров\n")
            f.write("\n")

            # Метрики клиентов
            f.write("👤 МЕТРИКИ КЛИЕНТОВ\n")
            f.write("-" * 80 + "\n")
            clients = metrics["clients"]
            f.write(f"Активных клиентов: {clients['total_active']}\n")
            f.write(f"Клиентов с заказами: {clients['clients_with_orders']}\n")
            f.write(
                f"Повторных клиентов: {clients['repeat_clients']} ({clients['repeat_client_percent']}%)\n"
            )
            f.write(
                f"Среднее заказов на клиента: {clients['avg_orders_per_client']}\n\n"
            )


def main():
    sql_file = "911_last.sql"

    print("=" * 80)
    print("РАСЧЕТ БИЗНЕС-МЕТРИК ИЗ ДАМПА БД")
    print("=" * 80)

    calculator = DatabaseMetricsCalculator(sql_file)
    calculator.parse_sql_dump()
    metrics = calculator.calculate_metrics()
    calculator.generate_report(metrics)

    print("\n✅ Готово!")


if __name__ == "__main__":
    main()
