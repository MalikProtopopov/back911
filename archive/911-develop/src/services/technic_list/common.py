from abc import ABC, abstractmethod
from io import TextIOWrapper

from src.services.technic_list.structs import ParsedBrandsAndModels


class TechnicListImporter(ABC):

    def import_technic(self, file: TextIOWrapper) -> ParsedBrandsAndModels:
        data = self.extract_data(file=file)
        parsed_data = self.parse_data(data=data)
        return parsed_data

    @abstractmethod
    def extract_data(
        self, file: TextIOWrapper
    ) -> list[dict[str, str | dict[str, str]]]: ...

    @abstractmethod
    def parse_data(self, data) -> ParsedBrandsAndModels: ...


class TechnicListBulkSaver(ABC):

    @abstractmethod
    def bulk_save_parsed_data(self, parsed_data: ParsedBrandsAndModels) -> None: ...
