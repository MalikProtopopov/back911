from rest_framework import serializers

from src.models.technic import TechnicCategory, Technic


class TechnicCategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = TechnicCategory
        fields: list[str] = ["id", "title"]


class TechnicCategoryIdProvideSerializer(serializers.ModelSerializer):
    class Meta:
        model = TechnicCategory
        fields: list[str] = ["id", "title"]
        extra_kwargs: dict[str, dict[str, bool]] = {
            "id": {"read_only": False, "required": False}
        }
        read_only_fields = ["title"]


class TechnicSerializer(serializers.ModelSerializer):

    class Meta:
        model = Technic
        fields: list[str] = ["id", "brand", "car_model", "category"]
        extra_kwargs: dict[str, dict[str, bool]] = {
            "id": {"read_only": False, "required": False}
        }

    def create(self, validated_data) -> Technic:
        technic = Technic.objects.create(**validated_data)
        return technic


class TechnicDetailSerializer(serializers.ModelSerializer):

    category = TechnicCategorySerializer(read_only=True)

    class Meta:
        model = Technic
        fields: list[str] = ["id", "brand", "car_model", "category"]
