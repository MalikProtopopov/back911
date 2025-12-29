from rest_framework import serializers

from src.models.mobile_app_version import MobileAppVersion


class MobileAppVersionSerializer(serializers.ModelSerializer):

    class Meta:
        model = MobileAppVersion
        fields = [
            "id",
            "ios_partner",
            "android_partner",
            "ios_client",
            "android_client",
        ]
