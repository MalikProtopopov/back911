from dataclasses import dataclass

from src.models import CarBrandList, CarModelList


@dataclass(slots=True, frozen=True)
class ParsedBrandsAndModels:
    brands: list[CarBrandList]
    models: list[CarModelList]
