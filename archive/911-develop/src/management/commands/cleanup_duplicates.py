from django.core.management import BaseCommand
from django.db import transaction
from django.db.models import Count, Min

from src.models import OptionPrice, PartnerService


class Command(BaseCommand):
    help = "Удаляет дубликаты из таблиц option_price_db и partner_service_db"

    def handle(self, *args, **options):
        self.cleanup_option_price_duplicates()
        self.cleanup_partner_service_duplicates()

    @transaction.atomic
    def cleanup_option_price_duplicates(self):
        self.stdout.write("Поиск дубликатов в option_price_db...")

        duplicates = (
            OptionPrice.objects.values("option_id", "city_id", "technic_category_id")
            .annotate(count=Count("id"), min_id=Min("id"))
            .filter(count__gt=1)
        )

        total_deleted = 0
        for duplicate in duplicates:
            deleted = (
                OptionPrice.objects.filter(
                    option_id=duplicate["option_id"],
                    city_id=duplicate["city_id"],
                    technic_category_id=duplicate["technic_category_id"],
                )
                .exclude(id=duplicate["min_id"])
                .delete()
            )
            total_deleted += deleted[0]

        self.stdout.write(
            self.style.SUCCESS(f"Удалено {total_deleted} дубликатов из option_price_db")
        )

    @transaction.atomic
    def cleanup_partner_service_duplicates(self):
        self.stdout.write("Поиск дубликатов в partner_service_db...")

        duplicates = (
            PartnerService.objects.values(
                "service_id", "partner_id", "technic_category_id"
            )
            .annotate(count=Count("id"), min_id=Min("id"))
            .filter(count__gt=1)
        )

        total_deleted = 0
        for duplicate in duplicates:
            deleted = (
                PartnerService.objects.filter(
                    service_id=duplicate["service_id"],
                    partner_id=duplicate["partner_id"],
                    technic_category_id=duplicate["technic_category_id"],
                )
                .exclude(id=duplicate["min_id"])
                .delete()
            )
            total_deleted += deleted[0]

        self.stdout.write(
            self.style.SUCCESS(
                f"Удалено {total_deleted} дубликатов из partner_service_db"
            )
        )
