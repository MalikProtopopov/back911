from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry

from src.models.working_zone import WorkingZone


@registry.register_document
class WorkingZoneDocument(Document):
    area_coordinates = fields.GeoShapeField()

    class Index:
        name = "working_zone"
        settings = {
            "number_of_shards": 1,
            "number_of_replicas": 0,
        }

    class Django:
        model = WorkingZone
        fields = [
            "title",
            "departure_price",
            "fuel_delivery_price",
            "location_status",
        ]

    def prepare_area_coordinates(self, instance):
        return {"type": "polygon", "coordinates": [instance.area_coordinates]}
