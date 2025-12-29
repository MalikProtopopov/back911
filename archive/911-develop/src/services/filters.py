import django_filters
from django.db.models import QuerySet, Q, OuterRef, Exists
from django_filters import NumberFilter
from rest_framework.request import Request

from src.models import Partner, PartnerService, OptionPrice
from src.models import QuestionAnswer, PartnerServiceOption
from src.models.option import OrderOption
from src.models.order import Order, OrderConditions
from src.models.review import Review


class PartnerFilter(django_filters.FilterSet):
    services = NumberFilter(method="filter_services")

    class Meta:
        model = Partner
        fields = [
            "verify",
            "city",
            "is_working",
            "services",
        ]

    def filter_services(self, queryset, name, value):
        return queryset.filter(services__service_id=value)


class PartnerVerifyServiceAndTechnicCategoryFilter(django_filters.FilterSet):
    class Meta:
        model = PartnerService
        fields = {
            "verify_status": ["exact"],
            "service": ["exact"],
            "technic_category": ["exact"],
        }


class PartnerVerifyServiceStatusAndCityFilter(django_filters.FilterSet):
    city = django_filters.CharFilter(field_name="partner__city")

    class Meta:
        model = PartnerService
        fields = {
            "verify_status": ["exact"],
            "service": ["exact"],
            "partner__city": ["exact"],
        }


class PartnerVerifyServiceAndCityFilter(django_filters.FilterSet):
    city = django_filters.CharFilter(field_name="partner__city")

    class Meta:
        model = PartnerService
        fields = {"service": ["exact"], "partner__city": ["exact"]}


class PartnerCityFilter(django_filters.FilterSet):
    class Meta:
        model = Partner
        fields = {
            "city": ["exact"],
        }


class QuestionAnswerFilter(django_filters.FilterSet):
    class Meta:
        model = QuestionAnswer
        fields = {
            "questioner": ["exact"],
        }


class ServiceCategoryFilter(django_filters.FilterSet):
    class Meta:
        model = OptionPrice
        fields = {"option__service_id": ["exact"], "technic_category_id": ["exact"]}


class ServiceCategoryCityFilter(django_filters.FilterSet):
    class Meta:
        model = OptionPrice
        fields = {
            "option__service_id": ["exact"],
            "technic_category_id": ["exact"],
            "city_id": ["exact"],
        }


class ServiceCategoryZoneFilter(django_filters.FilterSet):
    working_zone = django_filters.CharFilter(field_name="city__working_zones")

    class Meta:
        model = OptionPrice
        fields = {
            "option__service_id": ["exact"],
            "technic_category_id": ["exact"],
        }


class ConditionFilter(django_filters.FilterSet):
    working_zone = django_filters.CharFilter(method="filter_working_zone")

    class Meta:
        model = OrderConditions
        fields = ["condition_type", "working_zone"]

    def filter_working_zone(self, queryset, name, value):
        return queryset.filter(city__working_zones__id=value).select_related(
            "city__working_zones",
        )


def order_custom_client_filter(request: Request, orders: QuerySet) -> QuerySet:
    if "order_kind" in request.query_params:
        order_kind = request.query_params["order_kind"]
        match order_kind:
            case "new":
                orders = orders.filter(status__in=["new"])
            case "in_work":
                orders = orders.filter(
                    status__in=["on_the_way", "in_progress", "on_confirmation"]
                )
            case "done":
                orders = orders.filter(status__in=["done", "cancelled"])
            case _:
                pass

    return orders.order_by("-id")


def order_custom_partner_filter(
    request: Request, orders: QuerySet, partner: Partner
) -> QuerySet[Order] | None:
    if "order_kind" in request.query_params:
        order_kind = request.query_params["order_kind"]
        match order_kind:
            case "new":
                if partner.is_working:
                    partner_service_options = PartnerServiceOption.objects.filter(
                        (
                            Q(
                                partner_service__technic_category_id=OuterRef(
                                    "order__technic_category_id"
                                )
                            )
                            | Q(partner_service__technic_category_id__isnull=True)
                        ),
                        partner_service__partner_id=partner.id,
                        partner_service__partner__city_id=partner.city_id,
                        partner_service__verify_status=PartnerService.VerifyStatuses.confirmed,
                        option_id=OuterRef("option_id"),
                        partner_service__service_id=OuterRef("order__service_id"),
                    )
                    order_options = (
                        OrderOption.objects.annotate(
                            option_exists=Exists(partner_service_options)
                        )
                        .filter(option_exists=False)
                        .values_list("order_id", flat=True)
                    )
                    orders = orders.filter(
                        status=Order.OrderStatuses.new,
                        commission__lte=partner.commission_balance,
                        city_id=partner.city_id,
                    ).exclude(id__in=order_options)
                else:
                    orders = Order.objects.none()
            case "in_work":
                orders = orders.filter(
                    status__in=["on_the_way", "in_progress", "on_confirmation"],
                    partner_id=partner.id,
                )
            case "done":
                orders = orders.filter(
                    status__in=["done", "cancelled"], partner_id=partner.id
                )
            case _:
                pass

    return orders.order_by("-id")


class ReviewFilter(django_filters.FilterSet):
    class Meta:
        model = Review
        fields = {"rating": ["exact"]}


class OrderStatusAndServiceFilter(django_filters.FilterSet):
    class Meta:
        model = Order
        fields = {"status": ["exact"], "service": ["exact"]}
