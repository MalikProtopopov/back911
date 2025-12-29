from general_layout.models.abs_admin import AdminAbs


class Admin(AdminAbs):
    class Meta:
        db_table = "admin_db"
        verbose_name = "Администратор"
        verbose_name_plural = "Администраторы"

    def __str__(self):
        if self.first_name:
            return self.first_name
        if hasattr(self, "current_user"):
            return str(self.current_user)

    def delete(self, *args, **kwargs):
        if hasattr(self, "current_user"):
            user = self.current_user
            user.is_staff = False
            user.is_admin = False
            user.is_superuser = False
            user.save()

        super().delete(*args, **kwargs)
