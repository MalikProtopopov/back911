class FCMTokenNotificationMessages:
    """Для составления сообщений для нотификаций"""

    def __init__(self):
        self.title = None
        self.body = None
        self.data = None

    def get_accept_order_notification(self, first_name: str, last_name: str) -> None:
        self.title = "Ваш заказ принят"
        self.body = f"К вам приедет {first_name} {last_name}"
        self.data = {"type": "order", "value": "in_work"}

    def get_new_order_notification(self, service_title: str) -> None:
        self.title = "Новый заказ"
        self.body = service_title
        self.data = {"type": "order", "value": "new"}

    def get_chat_notification(
        self, first_name: str, message_text: str, order_id: int
    ) -> None:
        self.title = f"{first_name} - новое сообщение"
        self.body = message_text
        self.data = {"type": "chat", "chat_id": f"{order_id}", "title": first_name}

    def get_status_change_on_the_way_to_in_progress_notification(
        self, first_name: str, last_name: str
    ) -> None:
        self.title = "Работа начата"
        self.body = f"{first_name} {last_name} начал работу по заказу"
        self.data = {"type": "order", "value": "in_work"}

    def get_status_change_in_progress_to_on_confirmation_notification(
        self, first_name: str, last_name: str
    ) -> None:
        self.title = "Подтвердите выполнение работы"
        self.body = f"{first_name} {last_name} завершил работу по заказу"
        self.data = {"type": "order", "value": "in_work"}

    def get_status_change_on_confirmation_to_done_notifications(self) -> None:
        self.title = "Заказ выполнен"
        self.body = "Клиент подтвердил выполнение работы"
        self.data = {"type": "order", "value": "done"}

    def get_cancel_order_notification(self) -> None:
        self.title = "Заказ отменен"
        self.body = "Клиент отменил свой заказ"
        self.data = {"type": "order", "value": "done"}
