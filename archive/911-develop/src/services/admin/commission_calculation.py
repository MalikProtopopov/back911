from datetime import datetime, date
from decimal import Decimal
from typing import Dict, Tuple, Optional

from dateutil.relativedelta import relativedelta

from django.db.models import Sum

from src.models import Order


def calculate_date_range(
    period_type: str, date_from: Optional[date], date_to: Optional[date]
) -> Tuple[date, date]:
    """
    Вычисляет даты начала и окончания периода на основе типа периода.

    Args:
        period_type: Тип периода (custom, last_month, last_3_months, last_year)
        date_from: Начальная дата (для custom)
        date_to: Конечная дата (для custom)

    Returns:
        Tuple[date, date]: (date_from, date_to)
    """
    today = datetime.now().date()

    if period_type == "custom":
        if not date_from or not date_to:
            raise ValueError(
                "Для произвольного периода необходимо указать date_from и date_to"
            )
        return date_from, date_to
    elif period_type == "last_month":
        date_from = today - relativedelta(months=1)
        return date_from, today
    elif period_type == "last_3_months":
        date_from = today - relativedelta(months=3)
        return date_from, today
    elif period_type == "last_year":
        date_from = today - relativedelta(years=1)
        return date_from, today
    else:
        raise ValueError(f"Неизвестный тип периода: {period_type}")


def calculate_partner_commission(
    partner_id: int, date_from: date, date_to: date
) -> Dict:
    """
    Рассчитывает комиссию партнера за указанный период.

    Args:
        partner_id: ID партнера
        date_from: Начальная дата периода
        date_to: Конечная дата периода

    Returns:
        Dict с данными о комиссии: total_commission, orders_count, orders
    """
    orders = (
        Order.objects.filter(
            partner_id=partner_id,
            status=Order.OrderStatuses.done,
            datetime_created__date__gte=date_from,
            datetime_created__date__lte=date_to,
        )
        .exclude(status=Order.OrderStatuses.cancelled)
        .select_related("service")
        .order_by("-datetime_created")
    )

    total_result = orders.aggregate(total=Sum("commission"))
    total_commission = total_result["total"] or Decimal("0.00")

    orders_detail = []
    for order in orders:
        orders_detail.append(
            {
                "order_id": order.id,
                "date": order.datetime_created.date(),
                "commission": order.commission,
                "status": order.status,
                "service_title": order.service.title if order.service else None,
                "total_price": order.total_price,
            }
        )

    return {
        "total_commission": total_commission,
        "orders_count": orders.count(),
        "orders": orders_detail,
    }


def calculate_service_commissions(date_from: date, date_to: date) -> Dict:
    """
    Рассчитывает общие комиссии по всему сервису за указанный период.

    Args:
        date_from: Начальная дата периода
        date_to: Конечная дата периода

    Returns:
        Dict с данными о комиссиях: total_commission, orders_count
    """
    orders = Order.objects.filter(
        status=Order.OrderStatuses.done,
        datetime_created__date__gte=date_from,
        datetime_created__date__lte=date_to,
    ).exclude(status=Order.OrderStatuses.cancelled)

    total_service_commission = Decimal("0.00")
    for order in orders:
        service_commission = order.total_price - order.commission
        total_service_commission += service_commission

    return {
        "total_commission": total_service_commission,
        "orders_count": orders.count(),
    }
