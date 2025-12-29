from rest_framework import serializers

from src.models.fcmtoken import FCMToken


class FCMTokenSerializer(serializers.ModelSerializer):

    class Meta:
        model = FCMToken
        fields = ["id", "token", "device_id"]

    def create(self, validated_data):
        user_type = self.context.get("user_type")
        filter_kwargs = {"device_id": validated_data.get("device_id")}
        if user_type == "client":
            filter_kwargs.update({"client_id": self.context.get("user_id")})
        else:
            filter_kwargs.update({"partner_id": self.context.get("user_id")})
        token = FCMToken.objects.filter(**filter_kwargs).first()
        if token:
            token.token = validated_data.get("token")
            token.save()
        else:
            filter_kwargs.pop("device_id")
            token = FCMToken.objects.create(**validated_data, **filter_kwargs)

        return token
