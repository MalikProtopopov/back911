from rest_framework import serializers

from src.models.simple_models import Contacts


class ContactsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contacts
        fields = ["phone_number", "whatsapp_partner", "whatsapp_client", "telegram"]
