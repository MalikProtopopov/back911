from decimal import Decimal

from django.db import transaction, IntegrityError, InternalError
from django.db.models import Count, Q, QuerySet
from rest_framework.exceptions import ValidationError

from src.models import Partner, PartnerService, OptionPrice
from src.models.option import PartnerServiceOption, Option


class PartnerServiceRepository:
    """
    Class for create and update partner services and options
    """

    def __init__(
        self,
        partner: Partner,
        options_list: list[int],
        service_id: int,
        technic_category_id: int | None = None,
    ):
        self.partner = partner
        self.technic_category_id = technic_category_id
        self.service_id = service_id
        self.option_ids = self.validate_option_ids(options_list)

    def get_partner_service(self) -> PartnerService:
        return PartnerService.objects.filter(
            service_id=self.service_id,
            partner=self.partner,
            technic_category_id=self.technic_category_id,
        ).first()

    def validate_option_ids(self, option_ids: list[int]) -> list[int]:
        new_options_count = len(option_ids)
        existing_options_count = Option.objects.filter(
            id__in=option_ids, service_id=self.service_id
        ).count()
        if existing_options_count != new_options_count:
            raise ValidationError({"error_message": "Выбраны неверные опции"})

        options_in_city_count = OptionPrice.objects.filter(
            option_id__in=option_ids,
            city_id=self.partner.city_id,
            technic_category_id=self.technic_category_id,
        ).count()
        if options_in_city_count != new_options_count:
            raise ValidationError(
                {"error_message": "Выбранных опций нет в вашем городе"}
            )

        return option_ids

    @transaction.atomic
    def add_new_service(self) -> PartnerService:
        """
        0. Check if the partner already has this service
        1. If yes, raise an error
        2. Otherwise, create a new partner service
        """

        partner_service = self.get_partner_service()
        if partner_service:
            raise ValidationError({"error_message": "Услуга уже существует"})

        partner_service = PartnerService.objects.create(
            service_id=self.service_id,
            partner=self.partner,
            technic_category_id=self.technic_category_id,
        )
        return partner_service

    def create_new_options(
        self, options_to_add: set[int] | list[int], partner_service: PartnerService
    ) -> None:
        new_options = [
            PartnerServiceOption(option_id=option_id, partner_service=partner_service)
            for option_id in options_to_add
        ]
        PartnerServiceOption.objects.bulk_create(new_options)

    def delete_options(
        self, options_to_remove: set[int], partner_service: PartnerService
    ):
        PartnerServiceOption.objects.filter(
            option_id__in=options_to_remove, partner_service=partner_service
        ).delete()

    def get_options_to_add_and_remove(self, partner_service: PartnerService) -> tuple:
        current_options = PartnerServiceOption.objects.filter(
            partner_service=partner_service
        ).values_list("option_id", flat=True)

        current_option_set = set(current_options)
        new_option_set = set(self.option_ids)

        options_to_add = new_option_set - current_option_set
        options_to_remove = current_option_set - new_option_set
        return options_to_add, options_to_remove

    @transaction.atomic
    def update_new_options(self, partner_service: PartnerService) -> None:
        options_to_add, options_to_remove = self.get_options_to_add_and_remove(
            partner_service
        )
        self.create_new_options(options_to_add, partner_service)
        self.delete_options(options_to_remove, partner_service)
        partner_service.verify_status = PartnerService.VerifyStatuses.on_confirmation
        partner_service.save()

    @transaction.atomic
    def update_service(self, partner_service: PartnerService) -> None:
        try:
            with transaction.atomic():
                partner_service.technic_category_id = self.technic_category_id
                self.update_new_options(partner_service)
                partner_service.full_clean()
                partner_service.verify_status = (
                    PartnerService.VerifyStatuses.on_confirmation
                )
                partner_service.save()
        except (InternalError, IntegrityError):
            raise ValidationError({"error_message": "Услуга уже существует"})

    @transaction.atomic
    def add_service_and_options(self) -> PartnerService:
        partner_service = self.add_new_service()
        self.create_new_options(
            options_to_add=self.option_ids, partner_service=partner_service
        )
        return partner_service


def partner_queryset_with_annotated_orders():
    queryset = (
        Partner.objects.annotate(
            cancelled_orders=Count("orders", filter=Q(orders__status="cancelled")),
            accepted_orders=Count("orders", filter=~Q(orders__status="cancelled")),
        )
        .select_related("current_user", "city")
        .prefetch_related(
            "orders",
            "services",
        )
    )
    return queryset


def check_options_before_city_change(partner_id: int, city_id: int) -> None:
    partner_service_options = PartnerServiceOption.objects.filter(
        partner_service__partner_id=partner_id
    ).select_related("partner_service")
    query = Q()
    for partner_service_option in partner_service_options:
        query |= Q(
            option_id=partner_service_option.option_id,
            technic_category_id=partner_service_option.partner_service.technic_category_id,
        )
    city_options = OptionPrice.objects.filter(query, city_id=city_id)
    if city_options.count() < partner_service_options.count():
        raise ValidationError(
            {
                "error_message": "Ваши услуги не соответствуют выбранному городу. "
                "Пожалуйста, обратитесь к администратору"
            }
        )


def get_suitable_partner_ids(
    options: QuerySet | list[int],
    service_id: int,
    city_id: int,
    technic_category_id: int | None = None,
    order_commission: Decimal | None = None,
):
    order_options_count = len(options)

    if order_options_count == 0:
        return []

    filter_kwargs = {
        "verify_status": PartnerService.VerifyStatuses.confirmed,
        "service_id": service_id,
        "partner__city_id": city_id,
        "partner__is_working": True,
        "partner__verify": Partner.VerifyPartnerStatuses.confirmed,
    }

    if technic_category_id:
        filter_kwargs["technic_category_id"] = technic_category_id
    if order_commission:
        filter_kwargs["partner__commission_balance__gte"] = order_commission
    suitable_partners_ids = (
        PartnerService.objects.filter(**filter_kwargs)
        .annotate(
            matched_options_count=Count(
                "options",
                filter=Q(options__id__in=options),
            )
        )
        .filter(matched_options_count=order_options_count)
        .select_related("partner")
        .prefetch_related("options")
        .values_list("partner_id", flat=True)
    )
    return suitable_partners_ids


def accrue_profit_to_partner(
    partner: Partner,
    profit: Decimal,
):
    partner.profit += profit
    partner.save()
