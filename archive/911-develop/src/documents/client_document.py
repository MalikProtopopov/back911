from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry

from src.models import Client


@registry.register_document
class ClientDocument(Document):
    id = fields.IntegerField()
    first_name = fields.TextField(
        fields={"raw": fields.KeywordField(normalizer="case_insensitive")},
    )
    phone = fields.TextField(
        fields={"raw": fields.KeywordField(normalizer="case_insensitive")},
    )
    client_status = fields.KeywordField()
    datetime_created = fields.DateField()

    class Index:
        name = "client"
        settings = {
            "number_of_shards": 1,
            "number_of_replicas": 0,
            "analysis": {
                "normalizer": {
                    "case_insensitive": {
                        "type": "custom",
                        "filter": ["lowercase", "asciifolding"],
                    }
                }
            },
        }

    class Django:
        model = Client
        queryset = Client.objects.select_related("current_user")

    def prepare_phone(self, instance):
        if hasattr(instance, "current_user") and instance.current_user:
            return instance.current_user.phone
        return None

    def prepare_datetime_created(self, instance):
        if hasattr(instance, "current_user") and instance.current_user:
            return instance.current_user.datetime_created
        return None
