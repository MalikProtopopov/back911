from celery import shared_task

from src.services.sms_ru import SmsRu


@shared_task
def send_sms(phone: str, code: str, **kwargs) -> None:
    SmsRu().send_code(phone, code)
