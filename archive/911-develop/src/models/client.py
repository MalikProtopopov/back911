from general_layout.models.abs_client import ClientAbs


class Client(ClientAbs):
    class Meta:
        db_table = "client_db"
        verbose_name = "Клиент"
        verbose_name_plural = "Клиенты"

    def __str__(self):
        if self.first_name:
            return self.first_name
        elif hasattr(self, "current_user"):
            if self.current_user.phone:
                return self.current_user.phone
            else:
                return "No phone"
        else:
            return "No User"
