from django.core.management import BaseCommand

from src.models import Service


class Command(BaseCommand):
    help = "Заполняет таблицу услуг"

    def handle(self, *args, **options):
        data = [
            {"id": 1, "title": "Выездной шиномонтаж"},
            {"id": 2, "title": "Доставка топлива"},
            {"id": 3, "title": "Эвакуатор / манипулятор"},
            {"id": 4, "title": "Автовышка"},
        ]
        for service in data:
            Service.objects.get_or_create(
                id=service["id"], defaults={"title": service["title"]}
            )

        self.stdout.write(
            self.style.SUCCESS(
                "================Successfully services added================="
            )
        )
