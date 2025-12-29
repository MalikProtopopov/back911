from rest_framework import serializers

from src.models.simple_models import Rules


class RulesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rules
        fields = ["id", "rules"]
