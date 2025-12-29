from datetime import datetime

from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry

from src.models.partner import Partner
from src.models.order import Order
from src.models.service import PartnerService


@registry.register_document
class PartnerDocument(Document):
    id = fields.IntegerField()
    first_name = fields.TextField(
        fields={"raw": fields.KeywordField(normalizer="case_insensitive")},
    )
    last_name = fields.TextField(
        fields={"raw": fields.KeywordField(normalizer="case_insensitive")},
    )
    phone = fields.TextField(
        fields={"raw": fields.KeywordField(normalizer="case_insensitive")},
    )
    city = fields.ObjectField(
        properties={
            "id": fields.IntegerField(),
            "title": fields.TextField(
                fields={"raw": fields.KeywordField(normalizer="case_insensitive")}
            ),
        }
    )
    datetime_created = fields.DateField()
    accepted_orders = fields.IntegerField()
    cancelled_orders = fields.IntegerField()
    services = fields.NestedField(
        properties={
            "service_id": fields.IntegerField(),
        }
    )
    verify = fields.TextField()
    rating = fields.FloatField()
    photo = fields.KeywordField(index=False)
    is_working = fields.BooleanField()
    profit = fields.FloatField()

    class Index:
        name = "partner"
        settings = {
            "number_of_shards": 1,
            "number_of_replicas": 0,
            "analysis": {
                "normalizer": {
                    "case_insensitive": {
                        "type": "custom",
                        "filter": ["lowercase", "asciifolding"],
                    }
                },
            },
        }

    class Django:
        model = Partner

    def prepare_datetime_created(self, instance: Partner) -> datetime | None:
        if hasattr(instance, "current_user") and instance.current_user:
            return instance.current_user.datetime_created
        return None

    def prepare_phone(self, instance: Partner) -> str | None:
        if hasattr(instance, "current_user") and instance.current_user:
            return instance.current_user.phone
        return None

    def prepare_accepted_orders(self, instance: Partner) -> int:
        return instance.orders.filter(status=Order.OrderStatuses.done).count()

    def prepare_cancelled_orders(self, instance: Partner) -> int:
        return instance.orders.filter(status=Order.OrderStatuses.cancelled).count()

    def prepare_city(self, instance: Partner) -> dict:
        return {
            "id": instance.city.id,
            "title": instance.city.title,
        }

    def prepare_services(self, instance: Partner) -> list[dict]:
        return [
            {"service_id": ps.service_id}
            for ps in PartnerService.objects.filter(partner_id=instance.id)
        ]

    def prepare_photo(self, instance: Partner) -> str | None:
        if instance.photo:
            return instance.photo.url
        return None
