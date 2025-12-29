from decimal import Decimal

from django.db import transaction, InternalError, IntegrityError
from rest_framework.exceptions import ValidationError, NotFound

from src.models import Option, TechnicCategory, City, OptionPrice
from src.models.order import OrderConditions


def validate_option_price(
    option_id: int,
    technic_category_id: int | None,
    city_id: int,
) -> None:
    if not Option.objects.filter(id=option_id).first():
        raise ValidationError({"error_message": "Указанной опции не существует"})
    if technic_category_id:
        if not TechnicCategory.objects.filter(id=technic_category_id).first():
            raise ValidationError(
                {"error_message": "Указанной категории техники не существует"}
            )
    if not City.objects.filter(id=city_id).first():
        raise ValidationError({"error_message": "Указанного города не существует"})


def create_option_price(
    option_id: int,
    technic_category_id: int | None,
    city_id: int,
    amount: Decimal,
    order_conditions: list[dict[str, str | Decimal]],
) -> OptionPrice:
    validate_option_price(
        option_id=option_id,
        technic_category_id=technic_category_id,
        city_id=city_id,
    )

    if OptionPrice.objects.filter(
        option_id=option_id, city_id=city_id, technic_category_id=technic_category_id
    ).exists():
        raise ValidationError(
            {
                "error_message": "Цена для данной опции, города и категории техники уже существует"
            }
        )

    try:
        with transaction.atomic():
            new_option_price = OptionPrice.objects.create(
                option_id=option_id,
                technic_category_id=technic_category_id,
                city_id=city_id,
                amount=amount,
            )
            order_conditions_to_create = [
                OrderConditions(
                    title=order_condition.get("title"),
                    condition_type=order_condition.get("condition_type"),
                    option=new_option_price,
                    additional_price=order_condition.get("additional_price"),
                )
                for order_condition in order_conditions
            ]
            OrderConditions.objects.bulk_create(order_conditions_to_create)
    except (InternalError, IntegrityError):
        raise ValidationError({"error_message": "Ошибка"})

    return new_option_price


def update_option_price(
    option_price_id: int,
    option_id: int,
    technic_category_id: int | None,
    city_id: int,
    amount: Decimal,
    order_conditions_to_create: list[dict[str, str | int | Decimal]],
    order_conditions_to_update: list[dict[str, str | Decimal]],
    order_conditions_to_delete: list[dict[str, int | str]],
) -> OptionPrice:
    option_price: OptionPrice | None = OptionPrice.objects.filter(
        id=option_price_id
    ).first()
    if not option_price:
        raise NotFound
    validate_option_price(
        option_id=option_id,
        technic_category_id=technic_category_id,
        city_id=city_id,
    )
    if (
        OptionPrice.objects.filter(
            option_id=option_id,
            city_id=city_id,
            technic_category_id=technic_category_id,
        )
        .exclude(id=option_price_id)
        .exists()
    ):
        raise ValidationError(
            {
                "error_message": "Цена для данной опции, города и категории техники уже существует"
            }
        )

    try:
        with transaction.atomic():
            option_price.option_id = option_id
            option_price.technic_category_id = technic_category_id
            option_price.city_id = city_id
            option_price.amount = amount
            option_price.save()
            to_create = [
                OrderConditions(
                    title=order_condition.get("title"),
                    condition_type=order_condition.get("condition_type"),
                    option=option_price,
                    additional_price=order_condition.get("additional_price"),
                )
                for order_condition in order_conditions_to_create
            ]
            OrderConditions.objects.bulk_create(to_create)
            to_update = []
            for order_condition in order_conditions_to_update:
                order_condition_to_update: OrderConditions = (
                    OrderConditions.objects.filter(id=order_condition["id"])
                ).first()
                if (
                    not order_condition_to_update
                    or order_condition_to_update.option != option_price
                ):
                    raise ValidationError()
                order_condition_to_update.title = order_condition.get("title")
                order_condition_to_update.condition_type = order_condition.get(
                    "condition_type"
                )
                order_condition_to_update.additional_price = order_condition.get(
                    "additional_price"
                )
                to_update.append(order_condition_to_update)
            OrderConditions.objects.bulk_update(
                to_update,
                [
                    "title",
                    "condition_type",
                    "additional_price",
                ],
            )
            ids_to_delete = [
                order_condition["id"] for order_condition in order_conditions_to_delete
            ]
            OrderConditions.objects.filter(id__in=ids_to_delete).delete()
    except (InternalError, IntegrityError):
        raise ValidationError({"error_message": "Ошибка"})
    return option_price
