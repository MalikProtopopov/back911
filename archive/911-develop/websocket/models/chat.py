from celery import chain
from django.db import models

from src.fcmtoken.fcm_notif_messages import FCMTokenNotificationMessages
from src.tasks.fcmtoken_tasks import send_notifications_to_tokens
from websocket.tasks import get_chat_token


class ChatRoom(models.Model):

    class Meta:
        db_table = "chatroom"
        verbose_name = "Комната чата"
        verbose_name_plural = "Комнаты чатов"
        ordering = ["-pk"]

    order = models.OneToOneField(
        "src.Order",
        related_name="chat_room",
        verbose_name="Заказ",
        db_index=True,
        on_delete=models.PROTECT,
    )
    mute = models.BooleanField(
        editable=True,
        default=False,
        verbose_name="Отключить уведомления",
    )
    is_active = models.BooleanField(
        editable=True,
        default=True,
        verbose_name="Активна",
    )

    def __str__(self) -> str:
        return f"Комната чата №{self.pk}, по заказу {self.order}."


class ChatMessage(models.Model):

    class Meta:
        db_table = "chatmessage"
        verbose_name = "Сообщение чата"
        verbose_name_plural = "Сообщения чата"

    class UserTypeStatuses(models.TextChoices):
        client = "client", "Клиент"
        partner = "partner", "Партнер"

    chat_room = models.ForeignKey(
        ChatRoom, on_delete=models.PROTECT, db_index=True, related_name="chat_messages"
    )
    author = models.ForeignKey("users.CustomUser", on_delete=models.PROTECT)
    content = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    user_type = models.CharField(
        max_length=50,
        choices=UserTypeStatuses.choices,
        null=True,
        blank=True,
        verbose_name="Тип пользователя",
    )

    def save(self, *args, **kwargs):
        super(ChatMessage, self).save(*args, **kwargs)

        self._send_chat_push_notification()

    def _get_sender_first_name(self):
        """
        Получить имя отправителя
        """
        return (
            self.author.partner.first_name
            if self.user_type == self.UserTypeStatuses.partner
            else self.author.client.first_name
        )

    def _get_recipient_id(self):
        """
        Получить id, кому отправляется сообщение
        """
        return (
            self.chat_room.order.client_id
            if self.user_type == self.UserTypeStatuses.partner
            else self.chat_room.order.partner_id
        )

    def _create_message_data(self):
        """
        Создать сообщение для отправки
        """
        notification_message = FCMTokenNotificationMessages()
        first_name = self._get_sender_first_name()
        if not first_name:
            first_name = "Клиент"
        notification_message.get_chat_notification(
            first_name=first_name,
            message_text=self.content,
            order_id=self.chat_room.order_id,
        )
        return notification_message

    def _send_chat_push_notification(self):
        """
        Отправить пуш-уведомление
        """
        notification_message = self._create_message_data()
        recipient_id = self._get_recipient_id()
        chain(
            get_chat_token.s(
                client_id=(
                    recipient_id
                    if self.user_type == self.UserTypeStatuses.partner
                    else None
                ),
                partner_id=(
                    recipient_id
                    if self.user_type == self.UserTypeStatuses.client
                    else None
                ),
            )
            | send_notifications_to_tokens.s(vars(notification_message))
        ).apply_async()

    def __str__(self):
        return f"Сообщение от {str(self.author)}"
