from celery import shared_task, group

from src.fcmtoken.fcm_app import send_push_notification


@shared_task
def send_notifications_to_tokens(tokens: list[str], notification_message: dict) -> None:
    if not tokens:
        return
    notification_tasks = group(
        send_push_notification.s(
            token=token,
            title=notification_message["title"],
            body=notification_message["body"],
            data=notification_message["data"],
        )
        for token in tokens
    )

    notification_tasks.apply_async()
