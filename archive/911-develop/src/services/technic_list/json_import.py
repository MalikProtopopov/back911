import json
from io import TextIOWrapper

from django.db import transaction

from src.models import CarBrandList, CarModelList
from src.services.technic_list.common import TechnicListImporter, TechnicListBulkSaver
from src.services.technic_list.structs import ParsedBrandsAndModels


class JSONTechnicListImporter(TechnicListImporter):

    def extract_data(
        self, file: TextIOWrapper
    ) -> list[dict[str, str | dict[str, str]]]:
        data = json.load(file)
        return data

    def parse_data(
        self, data: list[dict[str, str | dict[str, str]]]
    ) -> ParsedBrandsAndModels:
        brands = []
        models = []
        for d in data:
            brand_obj = self._create_brand(brand_data=d)
            if brand_obj:
                brands.append(brand_obj)
                brand_models = d.get("models", [])
                for model in brand_models:
                    model_obj = self._create_model(
                        model_data=model,
                        brand=brand_obj,
                    )
                    if model_obj:
                        models.append(model_obj)
        return ParsedBrandsAndModels(
            brands=brands,
            models=models,
        )

    def _create_brand(self, brand_data: dict[str, str]) -> CarBrandList | None:
        brand_id = brand_data.get("id", None)
        brand_title = brand_data.get("name", None)
        brand_cyrillic_title = brand_data.get("cyrillic-name", None)
        if brand_id and brand_title and brand_cyrillic_title:
            brand_obj = CarBrandList(
                id=brand_id,
                title=brand_title,
                cyrillic_title=brand_cyrillic_title,
            )
            return brand_obj
        return None

    def _create_model(
        self,
        model_data: dict[str, str],
        brand: CarBrandList,
    ) -> CarModelList | None:
        model_id = model_data.get("id", None)
        model_title = model_data.get("name", None)
        model_cyrillic_title = model_data.get("cyrillic-name", None)
        if model_id and model_title and model_cyrillic_title:
            model_obj = CarModelList(
                id=model_id,
                title=model_title,
                cyrillic_title=model_cyrillic_title,
                brand_id=brand.id,
            )
            return model_obj
        return None


class TechnicListBulkSaverImpl(TechnicListBulkSaver):

    @transaction.atomic
    def bulk_save_parsed_data(self, parsed_data: ParsedBrandsAndModels) -> None:
        CarBrandList.objects.bulk_create(objs=parsed_data.brands)
        CarModelList.objects.bulk_create(objs=parsed_data.models)
