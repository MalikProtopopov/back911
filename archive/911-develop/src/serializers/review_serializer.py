from rest_framework import serializers

from src.models import Review, Order
from src.serializers.client_serializer import ClientNameWithPhoneSimpleSerializer
from src.serializers.partner_serializer import (
    PartnerSimplePhoneAndPhotoSerializer,
    PartnerSimpleSerializer,
)


class ReviewSerializer(serializers.ModelSerializer):

    partner = PartnerSimpleSerializer()

    class Meta:
        model = Review
        fields = ["comment", "rating", "partner"]

    def validate(self, data):
        partner_id = data.get("partner").get("id")
        orders_count = Order.objects.filter(
            partner_id=partner_id, client=self.context["client"]
        ).count()
        reviews_count = Review.objects.filter(
            partner_id=partner_id, client=self.context["client"]
        ).count()
        if reviews_count > orders_count:
            raise serializers.ValidationError(
                {"error_message": "Вы не можете оставить отзыв о данном партнере"}
            )

        return data

    def create(self, validated_data):
        partner_id = validated_data.pop("partner").get("id")
        client = self.context.get("client")
        review = Review.objects.create(
            client=client, partner_id=partner_id, **validated_data
        )
        return review


class ReviewListSerializer(serializers.ModelSerializer):
    client = ClientNameWithPhoneSimpleSerializer()
    partner = PartnerSimplePhoneAndPhotoSerializer()

    class Meta:
        model = Review
        fields = ["id", "client", "partner", "comment", "rating"]
