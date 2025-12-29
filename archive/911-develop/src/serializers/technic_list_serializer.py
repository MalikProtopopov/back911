from rest_framework import serializers

from src.models import CarModelList, CarBrandList


class TechnicListJSONInputFileSerializer(serializers.Serializer):
    file = serializers.FileField()

    def validate_file(self, value):
        if not value.name.endswith(".json"):
            raise serializers.ValidationError(
                "Неверный формат файла. Ожидается geojson."
            )
        return value


class CarModelListSerializer(serializers.ModelSerializer):

    class Meta:
        model = CarModelList
        fields = [
            "id",
            "title",
            "cyrillic_title",
        ]


class CarBrandListSerializer(serializers.ModelSerializer):

    models = CarModelListSerializer(
        many=True,
        required=True,
    )

    class Meta:
        model = CarBrandList
        fields = ["id", "title", "cyrillic_title", "models"]


class CarModelForCreateBrand(serializers.Serializer):
    title = serializers.CharField()
    cyrillic_title = serializers.CharField()


class CarModelForUpdateBrand(serializers.Serializer):
    id = serializers.CharField(required=True)
    title = serializers.CharField()
    cyrillic_title = serializers.CharField()


class CreateCarBrandSerializer(serializers.Serializer):
    title = serializers.CharField()
    cyrillic_title = serializers.CharField()
    models = CarModelForCreateBrand(many=True)


class UpdateCarBrandSerializer(serializers.Serializer):
    title = serializers.CharField()
    cyrillic_title = serializers.CharField()
    models_to_create = CarModelForCreateBrand(many=True)
    models_to_update = CarModelForUpdateBrand(many=True)
    models_to_delete = serializers.ListField()
