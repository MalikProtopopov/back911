from general_layout.models.abs_simple_models import (
    QuestionAnswerAbs,
    ContactsAbs,
    RulesAbs,
)


class QuestionAnswer(QuestionAnswerAbs):

    class Meta:
        db_table = "question_answer_db"
        verbose_name = "Вопросы и ответы"
        verbose_name_plural = "Вопросы и ответы"


class Contacts(ContactsAbs):

    class Meta:
        db_table = "contacts_db"
        verbose_name = "Контакты"
        verbose_name_plural = "Контакты"


class Rules(RulesAbs):
    class Meta:
        db_table = "rules_db"
        verbose_name = "Правила пользования"
        verbose_name_plural = "Правила пользования"
