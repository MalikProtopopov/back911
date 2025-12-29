from django.db import models


class QuestionAnswerAbs(models.Model):
    """Вопрос-ответ"""

    class QuestionerType(models.TextChoices):
        partner = "partner", "Партнер"
        client = "client", "Клиент"

    class Meta:
        abstract = True

    question = models.CharField(max_length=255, verbose_name="Вопрос")
    answer = models.TextField(verbose_name="Ответ")
    questioner = models.CharField(
        choices=QuestionerType.choices, verbose_name="Тип спрашивающего"
    )


class RulesAbs(models.Model):
    """Правила"""

    class Meta:
        abstract = True

    rules = models.TextField(verbose_name="Правила пользования")


class ContactsAbs(models.Model):
    """Контакты"""

    class Meta:
        abstract = True

    phone_number = models.CharField(max_length=50, verbose_name="Номер телефона")
    whatsapp_partner = models.URLField(
        verbose_name="URL WhatsApp партнера", blank=True, null=True
    )
    telegram = models.URLField(verbose_name="URL Telegram")
    whatsapp_client = models.URLField(
        verbose_name="URL WhatsApp клиента", blank=True, null=True
    )
