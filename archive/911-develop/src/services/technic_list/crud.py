from django.db import transaction, InternalError, IntegrityError
from rest_framework.exceptions import ValidationError, NotFound

from src.models import CarBrandList, CarModelList


def create_car_brand(
    title: str,
    cyrillic_title: str,
    models: list[dict[str, str]],
) -> CarBrandList:
    car_brand_exists = CarBrandList.objects.filter(id=title).first()
    if car_brand_exists:
        raise ValidationError({"error_message": "Бренд уже существует"})
    try:
        with transaction.atomic():
            new_car_brand = CarBrandList.objects.create(
                id=title,
                title=title,
                cyrillic_title=cyrillic_title,
            )
            to_create = []
            for model in models:
                car_model_exists = CarModelList.objects.filter(
                    id=model.get("title")
                ).first()
                if car_model_exists:
                    raise ValidationError({"error_message": "Модель уже существует"})
                to_create.append(
                    CarModelList(
                        id=model.get("title"),
                        title=model.get("title"),
                        brand=new_car_brand,
                        cyrillic_title=model.get("cyrillic_title"),
                    )
                )

            CarModelList.objects.bulk_create(to_create)
    except (InternalError, IntegrityError):
        raise ValidationError()
    return new_car_brand


def update_car_brand(
    car_brand_id: str,
    title: str,
    cyrillic_title: str,
    models_to_create: list[dict[str, str]],
    models_to_update: list[dict[str, str]],
    models_to_delete: list[dict[str, str]],
) -> CarBrandList:
    car_brand: CarBrandList = CarBrandList.objects.filter(id=car_brand_id).first()
    if not car_brand:
        raise NotFound
    try:
        with transaction.atomic():
            car_brand_exists = CarBrandList.objects.filter(id=title).first()
            if car_brand_exists and car_brand.id != car_brand_exists.id:
                raise ValidationError({"error_message": "Бренд уже существует"})
            car_brand.id = title
            car_brand.title = title
            car_brand.cyrillic_title = cyrillic_title
            car_brand.save()
            to_create = []
            for model in models_to_create:
                car_model_exists = CarModelList.objects.filter(
                    id=model.get("title")
                ).first()
                if car_model_exists:
                    raise ValidationError({"error_message": "Модель уже существует"})
                to_create.append(
                    CarModelList(
                        id=model.get("title"),
                        title=model.get("title"),
                        brand=car_brand,
                        cyrillic_title=model.get("cyrillic_title"),
                    )
                )

            to_update = []
            for model in models_to_update:
                car_model: CarModelList = CarModelList.objects.filter(
                    id=model.get("id")
                ).first()
                if not car_model:
                    raise ValidationError({"error_message": "Модели не существует"})
                car_model_exists = CarModelList.objects.filter(
                    id=model.get("title")
                ).first()
                if car_model_exists:
                    raise ValidationError({"error_message": "Модель уже существует"})
                car_model.id = model.get("title")
                car_model.title = model.get("title")
                car_model.cyrillic_title = model.get("cyrillic_title")
                to_update.append(car_model)
            CarModelList.objects.bulk_update(to_update, ["title"])
            ids_to_delete = [model["id"] for model in models_to_delete]
            CarModelList.objects.filter(id__in=ids_to_delete).delete()
    except (InternalError, IntegrityError):
        raise ValidationError()
    return car_brand
