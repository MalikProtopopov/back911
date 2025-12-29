from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken


class PartnerJWTAuthentication(JWTAuthentication):
    def get_validated_token(self, raw_token):
        token = super().get_validated_token(raw_token)
        if token["aud"] != "partner":
            raise InvalidToken("Invalid audience for partner token")
        return token


class ClientJWTAuthentication(JWTAuthentication):
    def get_validated_token(self, raw_token):
        token = super().get_validated_token(raw_token)
        if token["aud"] != "client":
            raise InvalidToken("Invalid audience for client token")
        return token


class AdminJWTAuthentication(JWTAuthentication):
    def get_validated_token(self, raw_token):
        token = super().get_validated_token(raw_token)
        if token["aud"] != "admin":
            raise InvalidToken("Invalid audience for admin token")
        return token


class ClientOrPartnerJWTAuthentication(JWTAuthentication):
    def get_validated_token(self, raw_token):
        token = super().get_validated_token(raw_token)
        if token["aud"] != "client" and token["aud"] != "partner":
            raise InvalidToken("Invalid audience token")
        return token
