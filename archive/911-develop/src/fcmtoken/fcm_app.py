import firebase_admin
from celery import shared_task
from firebase_admin import credentials, messaging

from config.settings import FCMTOKEN_PATH

cred = credentials.Certificate(FCMTOKEN_PATH)
firebase_admin.initialize_app(cred)


@shared_task
def send_push_notification(token, title, body, data):
    message = messaging.Message(
        notification=messaging.Notification(title=title, body=body),
        token=token,
        data=data,
    )
    messaging.send(message)
