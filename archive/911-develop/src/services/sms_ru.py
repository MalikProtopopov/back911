import requests
from django.conf import settings


class SmsRu:
    """
    send sms
    sms ru
    """

    BASE_URL = settings.SMS_RU_URL
    TOKEN = settings.SMS_RU_TOKEN

    def send_code(self, phone_number: str, code: str):
        params = {
            "to": f"7{phone_number}",
            "msg": f"Ваш код авторизации: {code}",
            "api_id": self.TOKEN,
            "json": 1,
        }
        url = f"{self.BASE_URL}/sms/send"
        requests.get(url, params=params)
