from drf_spectacular.utils import extend_schema
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError, NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from config.jwt_auth import AdminJWTAuthentication
from src.elastic.search import search_coordinates_contains_point
from src.models import (
    City,
    TechnicCategory,
    OptionPrice,
    Client,
    CarBrandList,
)
from src.models.mobile_app_version import MobileAppVersion
from src.models.option import Option
from src.models.order import OrderConditions
from src.models.service import Service
from src.serializers.city_serializer import CitySimpleSerializer
from src.serializers.client_serializer import ClientNameWithPhoneSimpleSerializer
from src.serializers.condition_serializer import OrderConditionSerializer
from src.serializers.mobile_app_version import MobileAppVersionSerializer
from src.serializers.option_serializer import (
    OptionSerializer,
    OptionSimpleSerializer,
    OptionPriceSimpleSerializer,
)
from src.serializers.service_serializer import ServiceSimpleSerializer
from src.serializers.technic_list_serializer import (
    TechnicListJSONInputFileSerializer,
    CarBrandListSerializer,
)
from src.serializers.technic_serializer import TechnicCategorySerializer
from src.serializers.working_zone_serializer import CoordinatesInputSerializer
from src.services.filters import (
    ServiceCategoryFilter,
    ServiceCategoryZoneFilter,
    ServiceCategoryCityFilter,
)
from src.services.technic_list.json_import import (
    JSONTechnicListImporter,
    TechnicListBulkSaverImpl,
)


class UtilitiesViewSet(viewsets.ViewSet):
    """
    APIs for front fetch
    """

    queryset = Option.objects.all()

    @extend_schema(
        summary="Получить список опций",
        responses={200: status.HTTP_200_OK, 404: status.HTTP_404_NOT_FOUND},
    )
    @action(
        detail=False,
        methods=["get"],
        url_path="get-options",
        # permission_classes=[
        #     IsAuthenticated,
        # ],
    )
    def get_options(self, request) -> Response:
        query = Option.objects.all()
        serializer = OptionSerializer(query, many=True)
        return Response(serializer.data, status.HTTP_200_OK)

    @extend_schema(
        summary="Получить список услуг",
        responses={200: status.HTTP_200_OK, 404: status.HTTP_404_NOT_FOUND},
    )
    @action(
        detail=False,
        methods=["get"],
        url_path="get-services",
        permission_classes=[
            IsAuthenticated,
        ],
    )
    def get_services(self, request) -> Response:
        query = Service.objects.all()
        serializer = ServiceSimpleSerializer(query, many=True)
        return Response(serializer.data, status.HTTP_200_OK)

    @extend_schema(
        summary="Получить список городов",
        responses={200: status.HTTP_200_OK, 404: status.HTTP_404_NOT_FOUND},
    )
    @action(
        detail=False,
        methods=["get"],
        url_path="get-cities",
        permission_classes=[
            IsAuthenticated,
        ],
    )
    def get_list_of_cities(self, request) -> Response:
        queryset = City.objects.all().order_by("title")
        serializer = CitySimpleSerializer(queryset, many=True)
        return Response(serializer.data, status.HTTP_200_OK)

    @extend_schema(
        summary="Получить список категорий техники",
        responses={200: status.HTTP_200_OK, 404: status.HTTP_404_NOT_FOUND},
    )
    @action(
        detail=False,
        methods=["get"],
        url_path="get-technic-categories",
        permission_classes=[
            IsAuthenticated,
        ],
    )
    def get_list_of_technic_categories(self, request) -> Response:
        query = TechnicCategory.objects.all()
        serializer = TechnicCategorySerializer(query, many=True)
        return Response(serializer.data, status.HTTP_200_OK)

    @extend_schema(
        summary="Получить список категорий и опций для создания техники",
        responses={200: status.HTTP_200_OK, 404: status.HTTP_404_NOT_FOUND},
    )
    @action(
        detail=False,
        methods=["get"],
        url_path="get-categories-and-options-for-service",
        permission_classes=[
            IsAuthenticated,
        ],
    )
    def get_list_of_technic_categories_and_options_for_services(
        self, request
    ) -> Response:
        self.request: Request
        qs = OptionPrice.objects.filter(
            city=self.request.user.partner.city
        ).select_related("option")

        filterset = ServiceCategoryFilter(self.request.query_params, queryset=qs)
        if filterset.is_valid():
            qs = filterset.qs
        qs = qs.values_list("option_id", flat=True)
        result_data = {
            "services": ServiceSimpleSerializer(Service.objects.all(), many=True).data,
            "technic_categories": TechnicCategorySerializer(
                TechnicCategory.objects.all(),
                many=True,
            ).data,
            "options": OptionSimpleSerializer(
                Option.objects.filter(id__in=qs), many=True
            ).data,
        }
        return Response(result_data, status.HTTP_200_OK)

    @extend_schema(
        summary="Получить список категорий и опций для создания техники для админа",
        responses={200: status.HTTP_200_OK, 404: status.HTTP_404_NOT_FOUND},
    )
    @action(
        detail=False,
        methods=["get"],
        url_path="get-categories-and-options-for-service-admin",
        permission_classes=[
            IsAuthenticated,
        ],
    )
    def get_list_of_technic_categories_and_options_for_services_for_admin(
        self, request
    ) -> Response:
        self.request: Request
        qs = OptionPrice.objects.all().select_related("option")

        filterset = ServiceCategoryCityFilter(self.request.query_params, queryset=qs)
        if filterset.is_valid():
            qs = filterset.qs
        qs = qs.values_list("option_id", flat=True)
        result_data = {
            "services": ServiceSimpleSerializer(Service.objects.all(), many=True).data,
            "technic_categories": TechnicCategorySerializer(
                TechnicCategory.objects.all(),
                many=True,
            ).data,
            "options": OptionSimpleSerializer(
                Option.objects.filter(id__in=qs), many=True
            ).data,
        }
        return Response(result_data, status.HTTP_200_OK)

    @extend_schema(
        summary="Получить рабочую зону по координатам",
        request=CoordinatesInputSerializer,
        responses={200: status.HTTP_200_OK, 404: status.HTTP_404_NOT_FOUND},
    )
    @action(
        detail=False,
        methods=["post"],
        url_path="get-working-zone",
        permission_classes=[
            IsAuthenticated,
        ],
    )
    def get_working_zone_by_coordinates(self, request) -> Response:
        self.request: Request
        serializer = CoordinatesInputSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        coordinates = serializer.validated_data.get("coordinates")
        service_id = serializer.validated_data.get("service_id")
        working_zone_id, departure_price, fuel_delivery_price = (
            search_coordinates_contains_point(coordinates)
        )
        city = City.objects.filter(working_zones=working_zone_id).first()
        if not city:
            raise ValidationError(
                {"error_message": "Выбранные вами услуги недоступны по данному адресу"}
            )
        is_service_in_zone = (
            OptionPrice.objects.filter(
                city_id=city.id,
                option__service_id=service_id,
            )
            .select_related("option")
            .exists()
        )
        if is_service_in_zone:
            final_delivery_price = (
                fuel_delivery_price if service_id == 2 else departure_price
            )
            return Response(
                {
                    "working_zone_id": working_zone_id,
                    "city_id": city.id,
                    "departure_price": final_delivery_price,
                },
                status.HTTP_200_OK,
            )
        raise ValidationError(
            {"error_message": "Выбранные вами услуги недоступны по данному адресу"}
        )

    @extend_schema(
        summary="Получить список опций и условий для заказа",
        responses={200: status.HTTP_200_OK, 404: status.HTTP_404_NOT_FOUND},
    )
    @action(
        detail=False,
        methods=["get"],
        url_path="get-options-and-conditions-for-order",
        permission_classes=[
            IsAuthenticated,
        ],
    )
    def get_options_and_conditions_for_order(self, request) -> Response:
        self.request: Request
        options_qs = OptionPrice.objects.prefetch_related(
            "city__working_zones"
        ).select_related("option__service")
        conditions_qs = OrderConditions.objects.filter(
            condition_type=OrderConditions.ConditionTypes.fuel_type,
        )

        options_filter = ServiceCategoryZoneFilter(
            self.request.query_params,
            options_qs,
        )

        if options_filter.is_valid():
            options_qs = options_filter.qs

        response = {
            "options": OptionPriceSimpleSerializer(
                options_qs,
                many=True,
            ).data,
            "fuel_conditions": OrderConditionSerializer(
                conditions_qs.order_by("title"),
                many=True,
            ).data,
        }
        return Response(response, status.HTTP_200_OK)

    @extend_schema(
        summary="Получение клиентов для заказа",
        responses={200: status.HTTP_200_OK, 404: status.HTTP_404_NOT_FOUND},
    )
    @action(
        detail=False,
        methods=["get"],
        url_path="order-clients",
        permission_classes=[IsAuthenticated],
        authentication_classes=[AdminJWTAuthentication],
    )
    def get_clients_for_admin_order(self, request) -> Response:
        self.request: Request
        clients = Client.objects.all().select_related("current_user")
        serializer = ClientNameWithPhoneSimpleSerializer(clients, many=True)
        return Response(serializer.data, status.HTTP_200_OK)

    @extend_schema(
        summary="Файл для добавления списка брендов и моделей",
        responses={
            201: status.HTTP_201_CREATED,
            400: status.HTTP_400_BAD_REQUEST,
        },
    )
    @action(
        detail=False,
        methods=["post"],
        url_path="create-car-brands",
        permission_classes=[IsAuthenticated],
        authentication_classes=[AdminJWTAuthentication],
    )
    def create_car_brands(self, request: Request) -> Response:
        self.request: Request
        serializer = TechnicListJSONInputFileSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        file = serializer.validated_data.get("file")
        parsed_data = JSONTechnicListImporter().import_technic(
            file=file,
        )
        TechnicListBulkSaverImpl().bulk_save_parsed_data(
            parsed_data=parsed_data,
        )
        return Response(
            {"success": True},
            status=status.HTTP_201_CREATED,
        )

    @extend_schema(
        summary="Список брендов и моделей",
        responses={
            404: status.HTTP_404_NOT_FOUND,
        },
    )
    @action(
        detail=False,
        methods=["get"],
        url_path="get-car-brands",
        permission_classes=[IsAuthenticated],
    )
    def get_car_brands(self, request: Request) -> Response:
        query = CarBrandList.objects.prefetch_related("models").order_by("title")
        serializer = CarBrandListSerializer(query, many=True)
        return Response(serializer.data, status.HTTP_200_OK)

    @extend_schema(
        summary="Получить версии устройств",
        responses={
            404: status.HTTP_404_NOT_FOUND,
        },
    )
    @action(
        detail=False,
        methods=["get"],
        url_path="get-app-versions",
    )
    def get_app_versions(self, request: Request) -> Response:
        app_version = MobileAppVersion.objects.first()
        if not app_version:
            raise NotFound
        serializer = MobileAppVersionSerializer(app_version)
        return Response(serializer.data, status.HTTP_200_OK)
