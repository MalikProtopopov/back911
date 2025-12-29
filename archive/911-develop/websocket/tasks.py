from celery import shared_task

from src.models.fcmtoken import FCMToken


@shared_task
def get_chat_token(**kwargs):
    tokens = FCMToken.objects.filter(**kwargs).values_list("token", flat=True)

    return list(tokens)
