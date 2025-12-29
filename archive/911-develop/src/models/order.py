from decimal import Decimal

from celery import chain
from django.db import models

from general_layout.models.abs_order import OrderAbs
from src.fcmtoken.fcm_notif_messages import FCMTokenNotificationMessages
from src.tasks.fcmtoken_tasks import send_notifications_to_tokens
from src.tasks.order_tasks import (
    send_new_order_ws_notification,
    get_order_member_tokens_task,
    get_suitable_partner_tokens,
)
from websocket.models.chat import ChatRoom


class Order(OrderAbs):

    class Meta:
        db_table = "order_db"
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"

    client = models.ForeignKey(
        "Client",
        related_name="orders",
        on_delete=models.PROTECT,
        verbose_name="Клиент",
        db_index=True,
    )
    partner = models.ForeignKey(
        "Partner",
        related_name="orders",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name="Партнер",
        db_index=True,
    )
    service = models.ForeignKey(
        "Service",
        related_name="orders",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        verbose_name="Услуга",
        db_index=True,
    )
    city = models.ForeignKey(
        "City",
        related_name="orders",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        verbose_name="Город",
        db_index=True,
    )
    options = models.ManyToManyField(
        "Option",
        related_name="orders",
        through="OrderOption",
        verbose_name="Опции",
    )
    technic_category = models.ForeignKey(
        "TechnicCategory",
        related_name="orders",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        verbose_name="Категория техники",
        db_index=True,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__partner_id = self.partner_id
        self.__status = self.status

    def save(self, *args, **kwargs):
        self.full_clean()
        is_new = bool(self.status == self.OrderStatuses.new)
        super(Order, self).save(*args, **kwargs)

        if is_new:
            self._handle_new_order()

        self._handle_partner_change()

        self._handle_status_change()

    def _handle_new_order(self):
        send_new_order_ws_notification.delay(self.pk)
        notification_message = FCMTokenNotificationMessages()
        notification_message.get_new_order_notification(
            service_title=self.service.title
        )
        self._send_notification(
            get_suitable_partner_tokens.s(order_id=self.pk), notification_message
        )

    def _handle_partner_change(self):
        if self.__partner_id != self.partner and not bool(self.__partner_id):
            ChatRoom.objects.get_or_create(order_id=self.id)
            notification_message = FCMTokenNotificationMessages()
            notification_message.get_accept_order_notification(
                first_name=self.partner.first_name, last_name=self.partner.last_name
            )
            self._send_notification(
                get_order_member_tokens_task.s(client_id=self.client_id),
                notification_message,
            )

    def _handle_status_change(self):
        status_transitions = {
            (
                self.OrderStatuses.on_the_way,
                self.OrderStatuses.in_progress,
            ): self._notify_on_the_way_to_in_progress,
            (
                self.OrderStatuses.in_progress,
                self.OrderStatuses.on_confirmation,
            ): self._notify_in_progress_to_on_confirmation,
            (
                self.OrderStatuses.on_confirmation,
                self.OrderStatuses.done,
            ): self._notify_on_confirmation_to_done_and_close_chat_room,
        }
        if self.status == self.OrderStatuses.cancelled:
            self._notify_cancelled()
            self._close_chat_room()
        else:
            transition_action = status_transitions.get((self.__status, self.status))
            if transition_action:
                transition_action()

    def _notify_on_the_way_to_in_progress(self):
        notification_message = FCMTokenNotificationMessages()
        notification_message.get_status_change_on_the_way_to_in_progress_notification(
            first_name=self.partner.first_name, last_name=self.partner.last_name
        )
        self._send_notification(
            get_order_member_tokens_task.s(client_id=self.client_id),
            notification_message,
        )

    def _notify_in_progress_to_on_confirmation(self):
        notification_message = FCMTokenNotificationMessages()
        notification_message.get_status_change_in_progress_to_on_confirmation_notification(
            first_name=self.partner.first_name, last_name=self.partner.last_name
        )
        self._send_notification(
            get_order_member_tokens_task.s(client_id=self.client_id),
            notification_message,
        )

    def _notify_on_confirmation_to_done_and_close_chat_room(self):
        notification_message = FCMTokenNotificationMessages()
        notification_message.get_status_change_on_confirmation_to_done_notifications()
        self._send_notification(
            get_order_member_tokens_task.s(partner_id=self.partner_id),
            notification_message,
        )
        self._close_chat_room()

    def _notify_cancelled(self):
        if self.partner_id:
            notification_message = FCMTokenNotificationMessages()
            notification_message.get_cancel_order_notification()
            self._send_notification(
                get_order_member_tokens_task.s(partner_id=self.partner_id),
                notification_message,
            )

    def _close_chat_room(self):
        chat_room = ChatRoom.objects.filter(order_id=self.id).first()
        if chat_room:
            chat_room.is_active = False
            chat_room.save()

    def _send_notification(self, task, notification_message):
        chain(
            task | send_notifications_to_tokens.s(vars(notification_message))
        ).apply_async()

    def set_commission_from_percent(self, commission_percent: Decimal) -> None:
        self.commission = round(self.total_price * commission_percent / 100, 2)


class OrderConditions(models.Model):

    class Meta:
        db_table = "order_condition_db"
        verbose_name = "Условия заказа"
        verbose_name_plural = "Условия заказа"

    class ConditionTypes(models.TextChoices):
        radius = "radius", "Радиус колеса"
        fuel_type = "fuel_type", "Тип топлива"

    title = models.CharField(max_length=255)
    condition_type = models.CharField(
        max_length=100,
        choices=ConditionTypes.choices,
    )
    option = models.ForeignKey(
        "OptionPrice",
        related_name="order_conditions",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        verbose_name="Опция",
        db_index=True,
    )
    additional_price = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal("0"),
        null=True,
        blank=True,
    )
