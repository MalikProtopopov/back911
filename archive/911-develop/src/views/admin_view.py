import geojson
from django.db import transaction, IntegrityError
from django.db.models import Prefetch, Count, Sum, Q, OuterRef, Subquery
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiParameter, inline_serializer
from rest_framework import serializers
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.generics import GenericAPIView, get_object_or_404
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK

from src.elastic.search import (
    search_for_partner,
    search_for_client,
    get_list_of_clients_for_admin_es,
    get_list_of_partners_for_admin_es,
)

from src.models import (
    Partner,
    PartnerService,
    Client,
    Order,
    TechnicCategory,
    City,
    Technic,
    WorkingZone,
    Service,
    Option,
    PartnerServiceOption,
    OptionPrice,
    CarBrandList,
)
from src.models.administrator import Admin
from src.models.balance import DepositMinimum
from src.models.mobile_app_version import MobileAppVersion
from src.models.order import OrderConditions
from src.models.review import Review
from src.models.simple_models import Contacts, QuestionAnswer, Rules
from src.serializers.admin_serializer import (
    CreateOrUpdateAdminSerializer,
    AdminListSerializer,
    CalculateCommissionRequestSerializer,
    CommissionResponseSerializer,
    ServiceCommissionResponseSerializer,
)
from src.serializers.balance_serializer import CreateDepositAndCommissionSerializer
from src.serializers.city_serializer import CityListAdminSerializer
from src.serializers.condition_serializer import CreateOrderConditionByAdminSerializer
from src.serializers.mobile_app_version import MobileAppVersionSerializer
from src.serializers.option_serializer import (
    OptionSerializer,
    OptionPriceSerializer,
    CreateOptionPriceSerializer,
    UpdateOptionPriceSerializer,
)
from src.serializers.order_serializer import (
    OrderListSerializer,
    OrderConditionSerializer,
    CreateOrderForAdminSerializer,
    ChangeOrderStatusSerializer,
)
from src.serializers.partner_serializer import (
    PartnerListOnConfirmationSerializer,
    PartnerInfoForAdminSerializer,
    CreateOrUpdatePartnerSerializer,
    PartnerSimplePhoneAndPhotoSerializer,
)
from src.serializers.client_serializer import (
    ClientListAdminSerializer,
    ClientDetailForAdminSerializer,
    CreateOrUpdateClientForAdminSerializer,
)
from src.serializers.contacts_serializer import ContactsSerializer
from src.serializers.question_answer_serializer import QuestionAnswerSerializer
from src.serializers.review_serializer import ReviewListSerializer
from src.serializers.rules_serializer import RulesSerializer
from src.serializers.service_serializer import (
    ServiceListAdminSerializer,
    UpdateServiceVerifyStatusSerializer,
    CreateServiceSerializer,
    PartnerServiceSerializer,
    ServiceForAdminSerializer,
    ServiceWithOptionPricesSerializer,
)
from src.serializers.technic_list_serializer import (
    CreateCarBrandSerializer,
    UpdateCarBrandSerializer,
    CarBrandListSerializer,
)
from src.serializers.technic_serializer import (
    TechnicCategorySerializer,
    TechnicSerializer,
)
from src.serializers.working_zone_serializer import (
    WorkingZoneFileUploadSerializer,
    WorkingZoneReadOnlySerializer,
    CityForAdminSerializer,
)
from websocket.serializers import MessageSerializer
from websocket.services import get_chat_history
from src.services.admin.access_policy import AdminAccessPolicy
from src.services.admin.commission_calculation import (
    calculate_partner_commission,
    calculate_service_commissions,
)
from src.services.admin.working_zones import update_working_zones
from src.services.filters import (
    OrderStatusAndServiceFilter,
    PartnerCityFilter,
    PartnerVerifyServiceStatusAndCityFilter,
    PartnerVerifyServiceAndCityFilter,
    QuestionAnswerFilter,
    ReviewFilter,
)
from src.services.option.crud import create_option_price, update_option_price
from src.services.order.order_orm import subtract_commission
from src.services.pagination import DefaultPagination
from config.jwt_auth import AdminJWTAuthentication
from src.services.partner.partner_orm import (
    partner_queryset_with_annotated_orders,
    PartnerServiceRepository,
    get_suitable_partner_ids,
)
from src.services.admin.partner_admin import get_partners_for_admin
from src.services.permissions import BaseAdminPermission
from src.services.technic_list.crud import create_car_brand, update_car_brand


class AdminViewSet(viewsets.ViewSet, GenericAPIView):
    queryset = Partner.objects.all()
    filter_backends = [DjangoFilterBackend]
    pagination_class = DefaultPagination
    permission_classes = (IsAuthenticated, IsAdminUser, BaseAdminPermission)

    @extend_schema(
        summary="Список партнеров для админки",
        responses={200: status.HTTP_200_OK, 404: status.HTTP_404_NOT_FOUND},
    )
    @action(
        detail=False,
        methods=["get"],
        url_path="list-of-partners-admin",
        authentication_classes=[AdminJWTAuthentication],
    )
    def get_list_of_partners_for_admin(self, request: Request) -> Response:
        search = request.query_params.get("search")
        page = int(request.query_params.get("page", 1))
        filters = {}
        for key in request.query_params:
            filters.update({key: request.query_params.get(key)})
        partners, total_count = get_list_of_partners_for_admin_es(
            search_query=search,
            page=page,
            per_page=self.pagination_class.page_size,
            filters=filters,
        )

        paginator = self.pagination_class()
        fake_queryset = [None] * total_count
        paginator.paginate_queryset(fake_queryset, request)
        return Response(
            {
                "count": total_count,
                "next": paginator.get_next_link(),
                "previous": paginator.get_previous_link(),
                "results": partners,
            }
        )

    @extend_schema(
        summary="Список всех партнеров для админки",
        responses={200: status.HTTP_200_OK, 404: status.HTTP_404_NOT_FOUND},
    )
    @action(
        detail=False,
        methods=["get"],
        url_path="list-of-all-partners-admin",
        authentication_classes=[AdminJWTAuthentication],
    )
    def get_list_of_all_partners_for_admin(self, request: Request) -> Response:
        search = request.query_params.get("search")
        filters = {}
        for key in request.query_params:
            if key != "search":
                filters.update({key: request.query_params.get(key)})

        partners, total_count = get_partners_for_admin(
            search_query=search,
            filters=filters,
        )

        return Response(
            {
                "count": total_count,
                "results": partners,
            }
        )

    @extend_schema(
        summary="Список партнеров на подтверждении для админки",
        responses={200: status.HTTP_200_OK, 404: status.HTTP_404_NOT_FOUND},
    )
    @action(
        detail=False,
        methods=["get"],
        url_path="list-of-partners-on-confirmation-admin",
        authentication_classes=[AdminJWTAuthentication],
    )
    def get_list_of_partners_on_confirmation_for_admin(self, request) -> Response:
        self.request: Request
        qs = self.queryset.filter(verify="on_confirmation").select_related(
            "city", "current_user"
        )
        filterset = PartnerCityFilter(self.request.query_params, queryset=qs)
        if filterset.is_valid():
            qs = filterset.qs

        if "search" in request.query_params:
            search_result = search_for_partner(request.query_params["search"])
            qs = qs.filter(id__in=search_result)

        page = self.paginate_queryset(
            qs.order_by("-current_user__datetime_created").select_related(
                "current_user"
            )
        )
        if page is not None:
            serializer = PartnerListOnConfirmationSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        return Response("", status.HTTP_200_OK)

    @extend_schema(
        summary="Создать нового админа",
        request=CreateOrUpdateAdminSerializer,
        responses={201: status.HTTP_201_CREATED, 400: status.HTTP_400_BAD_REQUEST},
    )
    @action(
        detail=False,
        methods=["post"],
        url_path="create-new-admin",
        authentication_classes=[AdminJWTAuthentication],
    )
    def create_new_admin(self, request) -> Response:
        self.request: Request
        serializer = CreateOrUpdateAdminSerializer(data=self.request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status.HTTP_201_CREATED)
        return Response(status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Детальная страница админа",
        responses={200: AdminListSerializer, 404: status.HTTP_404_NOT_FOUND},
    )
    @action(
        detail=True,
        methods=["get"],
        url_path="get-info-for-admin",
        authentication_classes=[AdminJWTAuthentication],
    )
    def get_info_for_admin(self, request, pk=None) -> Response:
        self.request: Request
        admin = Admin.objects.filter(pk=pk)
        if admin.exists():
            admin = admin.select_related("current_user").first()
            serializer = AdminListSerializer(admin)
            return Response(serializer.data, status.HTTP_200_OK)
        return Response(status.HTTP_404_NOT_FOUND)

    @extend_schema(
        summary="Редактирование администратора",
        responses={200: CreateOrUpdateAdminSerializer, 404: status.HTTP_404_NOT_FOUND},
    )
    @action(
        detail=True,
        methods=["patch"],
        url_path="update-info-for-admin",
        authentication_classes=[AdminJWTAuthentication],
    )
    def update_info_for_admin(self, request, pk=None) -> Response:
        self.request: Request
        admin = Admin.objects.filter(pk=pk).select_related("current_user").first()
        serializer = CreateOrUpdateAdminSerializer(
            admin, data=self.request.data, partial=True
        )
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status.HTTP_200_OK)
        return Response(status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Список админов",
        responses={200: status.HTTP_200_OK, 404: status.HTTP_404_NOT_FOUND},
    )
    @action(
        detail=False,
        methods=["get"],
        url_path="list-of-admins",
        authentication_classes=[AdminJWTAuthentication],
    )
    def get_list_of_admins(self, request) -> Response:
        self.request: Request
        qs = Admin.objects.all().select_related("current_user")
        page = self.paginate_queryset(qs.order_by("-current_user__datetime_created"))
        if page is not None:
            serializer = AdminListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        return Response("", status.HTTP_200_OK)

    @extend_schema(
        summary="Список услуг партнеров",
        responses={200: status.HTTP_200_OK, 404: status.HTTP_404_NOT_FOUND},
    )
    @action(
        detail=False,
        methods=["get"],
        url_path="list-of-services",
        authentication_classes=[AdminJWTAuthentication],
    )
    def get_list_of_services_admin(self, request) -> Response:
        self.request: Request
        qs = PartnerService.objects.select_related(
            "service", "technic_category", "partner__city", "partner__current_user"
        ).prefetch_related("options")

        if "search" in request.query_params:
            search_result = search_for_partner(request.query_params["search"])
            qs = qs.filter(partner__id__in=search_result)

        filterset = PartnerVerifyServiceStatusAndCityFilter(
            self.request.query_params, queryset=qs
        )
        if filterset.is_valid():
            qs = filterset.qs

        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = ServiceListAdminSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        return Response("", status.HTTP_200_OK)

    @extend_schema(
        summary="Список услуг партнеров на подтверждении",
        responses={200: status.HTTP_200_OK, 404: status.HTTP_404_NOT_FOUND},
    )
    @action(
        detail=False,
        methods=["get"],
        url_path="list-of-services-on-confirmation",
        authentication_classes=[AdminJWTAuthentication],
    )
    def get_list_of_services_on_confirmation_admin(self, request) -> Response:
        self.request: Request
        qs = (
            PartnerService.objects.filter(verify_status="on_confirmation")
            .select_related(
                "service",
                "technic_category",
                "partner__city",
                "partner__current_user",
            )
            .prefetch_related("options")
        )

        if "search" in request.query_params:
            search_result = search_for_partner(request.query_params["search"])
            qs = qs.filter(partner__id__in=search_result)

        filterset = PartnerVerifyServiceAndCityFilter(
            self.request.query_params, queryset=qs
        )
        if filterset.is_valid():
            qs = filterset.qs

        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = ServiceListAdminSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        return Response("", status.HTTP_200_OK)

    @extend_schema(
        summary="Изменение статуса услуги",
        responses={200: status.HTTP_200_OK, 400: status.HTTP_404_NOT_FOUND},
    )
    @action(
        detail=True,
        methods=["patch"],
        url_path="update-verify-status-for-service",
        authentication_classes=[AdminJWTAuthentication],
    )
    def update_verify_status_for_service(self, request, pk=None) -> Response:
        self.request: Request
        partner_service = PartnerService.objects.filter(pk=pk).first()
        admin: Admin = request.user.admin
        if not AdminAccessPolicy.can_approve_service(
            admin=admin, service=partner_service
        ):
            return Response({"detail": "Нет прав на редактирование услуги"}, status=403)
        if partner_service:
            serializer = UpdateServiceVerifyStatusSerializer(
                partner_service,
                data=self.request.data,
                partial=True,
            )
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(status.HTTP_400_BAD_REQUEST)
        else:
            return Response(status.HTTP_404_NOT_FOUND)

    @extend_schema(
        summary="Список клиентов",
        responses={200: ClientListAdminSerializer, 404: status.HTTP_404_NOT_FOUND},
    )
    @action(
        detail=False,
        methods=["get"],
        url_path="list-of-clients-admin",
        authentication_classes=[AdminJWTAuthentication],
    )
    def get_list_of_clients_for_admin(self, request):
        search = request.query_params.get("search")
        client_status = request.query_params.get("client_status")
        page = int(request.query_params.get("page", 1))
        page_size = self.pagination_class.page_size

        clients, total_count = get_list_of_clients_for_admin_es(
            search_query=search,
            status_filter=client_status,
            page=page,
            per_page=page_size,
        )

        paginator = self.pagination_class()
        fake_queryset = [None] * total_count
        paginator.paginate_queryset(fake_queryset, request)
        return Response(
            {
                "count": total_count,
                "next": paginator.get_next_link(),
                "previous": paginator.get_previous_link(),
                "results": clients,
            }
        )

    @extend_schema(
        summary="Информация о клиенте",
        responses={200: ClientDetailForAdminSerializer, 404: status.HTTP_404_NOT_FOUND},
    )
    @action(
        detail=True,
        methods=["get"],
        url_path="get-info-client-for-admin",
        authentication_classes=[AdminJWTAuthentication],
    )
    def get_info_client_for_admin(self, request, pk=None) -> Response:
        self.request: Request
        client = Client.objects.filter(pk=pk)
        if client.exists():
            client = (
                client.select_related("current_user")
                .prefetch_related(
                    "technics",
                    Prefetch(
                        "orders",
                        queryset=Order.objects.select_related(
                            "service", "technic_category", "partner__current_user"
                        ).prefetch_related("options"),
                    ),
                )
                .first()
            )
            serializer = ClientDetailForAdminSerializer(client)
            return Response(serializer.data, status.HTTP_200_OK)
        return Response(status.HTTP_404_NOT_FOUND)

    @extend_schema(
        summary="Добавить клиента",
        responses={
            201: CreateOrUpdateClientForAdminSerializer,
            400: status.HTTP_400_BAD_REQUEST,
        },
    )
    @action(
        detail=False,
        methods=["post"],
        url_path="add-client-by-admin",
        authentication_classes=[AdminJWTAuthentication],
    )
    def add_client_by_admin(self, request) -> Response:
        self.request: Request
        serializer = CreateOrUpdateClientForAdminSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({"success": False}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Изменить информацию о клиенте",
        request=CreateOrUpdateClientForAdminSerializer,
        responses={200: status.HTTP_200_OK, 400: status.HTTP_400_BAD_REQUEST},
    )
    @action(
        detail=True,
        methods=["patch"],
        url_path="update-client",
        authentication_classes=[AdminJWTAuthentication],
    )
    def update_client_by_admin(self, request, pk=None) -> Response:
        self.request: Request
        client = get_object_or_404(Client, pk=pk)
        serializer = CreateOrUpdateClientForAdminSerializer(
            client,
            data=self.request.data,
            partial=True,
        )
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Изменить технику клиента",
        request=TechnicSerializer,
        responses={200: status.HTTP_200_OK, 400: status.HTTP_400_BAD_REQUEST},
    )
    @action(
        detail=True,
        methods=["patch"],
        url_path="update-client-technic",
        authentication_classes=[AdminJWTAuthentication],
    )
    def update_client_technic_by_admin(self, request, pk=None):
        self.request: Request
        client = get_object_or_404(Client, pk=pk)
        try:
            with transaction.atomic():
                Technic.objects.filter(client=client).delete()
                serializer = TechnicSerializer(data=self.request.data, many=True)
                serializer.is_valid(raise_exception=True)
                serializer.save(client=client)
            return Response(serializer.data, status.HTTP_200_OK)
        except IntegrityError as e:
            return Response({"success": False}, status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Информация о партнере",
        responses={
            200: PartnerInfoForAdminSerializer,
            404: status.HTTP_404_NOT_FOUND,
        },
    )
    @action(
        detail=True,
        methods=["get"],
        url_path="get-info-partner-for-admin",
        authentication_classes=[AdminJWTAuthentication],
    )
    def get_info_partner_for_admin(self, request, pk=None) -> Response:
        self.request: Request
        admin: Admin = request.user.admin
        partner = partner_queryset_with_annotated_orders().get(pk=pk)
        if not AdminAccessPolicy.can_view_or_edit_partner(admin, partner):
            return Response(
                {"detail": "Нет прав на редактирование партнёра"}, status=403
            )
        if not AdminAccessPolicy.can_view_or_edit_partner(admin, partner):
            return Response(
                {"detail": "Нет прав на редактирование партнёра"}, status=403
            )
        serializer = PartnerInfoForAdminSerializer(partner)
        return Response(serializer.data)

    @extend_schema(
        summary="Добавить партнера",
        request=CreateOrUpdatePartnerSerializer,
        responses={
            201: CreateOrUpdatePartnerSerializer,
            400: status.HTTP_400_BAD_REQUEST,
        },
    )
    @action(
        detail=False,
        methods=["post"],
        url_path="add-partner-by-admin",
        authentication_classes=[AdminJWTAuthentication],
    )
    def add_partner_by_admin(self, request) -> Response:
        self.request: Request
        serializer = CreateOrUpdatePartnerSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({"success": False}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Изменить информацию о партнере",
        request=CreateOrUpdatePartnerSerializer,
        responses={
            200: CreateOrUpdatePartnerSerializer,
            400: status.HTTP_400_BAD_REQUEST,
        },
    )
    @action(
        detail=True,
        methods=["patch"],
        url_path="update-partner",
        authentication_classes=[AdminJWTAuthentication],
    )
    def update_partner(self, request, pk=None) -> Response:
        self.request: Request
        partner = get_object_or_404(Partner, pk=pk)
        admin: Admin = request.user.admin
        if not AdminAccessPolicy.can_view_or_edit_partner(admin=admin, partner=partner):
            return Response(
                {"detail": "Нет прав на редактирование партнёра"}, status=403
            )
        serializer = CreateOrUpdatePartnerSerializer(
            partner,
            data=self.request.data,
            partial=True,
        )
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Создать / изменить/ удалить услуги партнера",
        request=CreateServiceSerializer,
        responses={200: status.HTTP_200_OK, 400: status.HTTP_400_BAD_REQUEST},
    )
    @action(
        detail=True,
        methods=["patch"],
        url_path="update-partner-services",
        authentication_classes=[AdminJWTAuthentication],
    )
    def update_partner_services(self, request, pk=None) -> Response:
        self.request: Request
        partner = Partner.objects.filter(pk=pk).first()
        response_data = []
        try:
            with transaction.atomic():
                PartnerService.objects.filter(partner=partner).delete()
                for data in self.request.data:
                    serializer = CreateServiceSerializer(data=data)
                    serializer.is_valid(raise_exception=True)
                    partner_service = PartnerServiceRepository(
                        partner=partner, **data
                    ).add_service_and_options()
                    partner_service.verify_status = (
                        PartnerService.VerifyStatuses.confirmed
                    )
                    partner_service.save()
                    response_data.append(PartnerServiceSerializer(partner_service).data)
                return Response(response_data, status.HTTP_200_OK)
        except Exception as e:
            return Response({"success": False}, status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Добавить/изменить контакты",
        responses={200: ContactsSerializer, 400: status.HTTP_400_BAD_REQUEST},
    )
    @action(
        detail=False,
        methods=["post"],
        url_path="add-or-update-contacts-by-admin",
        authentication_classes=[AdminJWTAuthentication],
    )
    def add_or_update_contacts_by_admin(self, request) -> Response:
        self.request: Request
        contacts = Contacts.objects.first()
        if contacts:
            serializer = ContactsSerializer(
                contacts, data=self.request.data, partial=True
            )
        else:
            serializer = ContactsSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({"success": False}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Получить контакты",
        responses={200: ContactsSerializer, 404: status.HTTP_404_NOT_FOUND},
    )
    @action(
        detail=False,
        methods=["get"],
        url_path="get-contacts",
        authentication_classes=[AdminJWTAuthentication],
    )
    def get_contacts_for_admin(self, request) -> Response:
        self.request: Request
        contacts = Contacts.objects.first()
        if contacts:
            serializer = ContactsSerializer(contacts)
            return Response(serializer.data, status.HTTP_200_OK)
        return Response("", status.HTTP_200_OK)

    @extend_schema(
        summary="Добавить вопрос/ответ",
        responses={201: QuestionAnswerSerializer, 400: status.HTTP_404_NOT_FOUND},
    )
    @action(
        detail=False,
        methods=["post"],
        url_path="add-question-answer-by-admin",
        authentication_classes=[AdminJWTAuthentication],
    )
    def add_question_answer_by_admin(self, request) -> Response:
        self.request: Request
        serializer = QuestionAnswerSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({"success": False}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Изменить вопрос/ответ",
        responses={200: QuestionAnswerSerializer, 400: status.HTTP_400_BAD_REQUEST},
    )
    @action(
        detail=True,
        methods=["patch"],
        url_path="update-question-answer",
        authentication_classes=[AdminJWTAuthentication],
    )
    def update_question_answer_for_admin(self, request, pk=None) -> Response:
        self.request: Request
        question_answer = get_object_or_404(QuestionAnswer, pk=pk)
        serializer = QuestionAnswerSerializer(
            question_answer, data=self.request.data, partial=True
        )
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Получить вопрос/ответ",
        responses={200: QuestionAnswerSerializer, 404: status.HTTP_404_NOT_FOUND},
    )
    @action(
        detail=True,
        methods=["get"],
        url_path="get-question-answer",
        authentication_classes=[AdminJWTAuthentication],
    )
    def get_question_answer_for_admin(self, request, pk=None) -> Response:
        self.request: Request
        question_answer = QuestionAnswer.objects.filter(pk=pk)
        if question_answer.exists():
            serializer = QuestionAnswerSerializer(question_answer.first())
            return Response(serializer.data, status.HTTP_200_OK)
        return Response(status.HTTP_404_NOT_FOUND)

    @extend_schema(
        summary="Получить список вопросов/ответов",
        responses={200: QuestionAnswerSerializer, 404: status.HTTP_404_NOT_FOUND},
    )
    @action(
        detail=False,
        methods=["get"],
        url_path="get-list-question-answer",
        authentication_classes=[AdminJWTAuthentication],
    )
    def get_list_question_answer_for_admin(self, request) -> Response:
        self.request: Request
        queryset = QuestionAnswer.objects.all()
        filterset = QuestionAnswerFilter(self.request.query_params, queryset=queryset)
        if filterset.is_valid():
            queryset = filterset.qs
        serializer = QuestionAnswerSerializer(queryset, many=True)
        return Response(serializer.data, status.HTTP_200_OK)

    @extend_schema(
        summary="Удалить вопрос/ответ",
        responses={204: status.HTTP_204_NO_CONTENT, 404: status.HTTP_404_NOT_FOUND},
    )
    @action(
        detail=True,
        methods=["delete"],
        url_path="delete-question-answer",
        authentication_classes=[AdminJWTAuthentication],
    )
    def delete_question_answer_for_admin(self, request, pk=None) -> Response:
        self.request: Request
        question_answer = QuestionAnswer.objects.filter(pk=pk)
        if question_answer.exists():
            question_answer.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_404_NOT_FOUND)

    @extend_schema(
        summary="Получить правила пользования",
        responses={200: RulesSerializer, 404: status.HTTP_404_NOT_FOUND},
    )
    @action(
        detail=False,
        methods=["get"],
        url_path="get-rules",
        authentication_classes=[],
        permission_classes=[AllowAny],
    )
    def get_rules_for_admin(self, request) -> Response:
        self.request: Request
        rules = Rules.objects.first()
        if rules:
            serializer = RulesSerializer(rules)
            return Response(serializer.data, status.HTTP_200_OK)
        return Response("", status.HTTP_200_OK)

    @extend_schema(
        summary="Добавить/изменить правила пользования",
        responses={201: RulesSerializer, 400: status.HTTP_400_BAD_REQUEST},
    )
    @action(
        detail=False,
        methods=["post"],
        url_path="add-or-update-rules-by-admin",
        authentication_classes=[AdminJWTAuthentication],
    )
    def add_or_update_rules_by_admin(self, request) -> Response:
        self.request: Request
        rules = Rules.objects.first()
        if rules:
            serializer = RulesSerializer(rules, data=self.request.data, partial=True)
        else:
            serializer = RulesSerializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Список отзывов о партнерах.",
        responses={200: ReviewListSerializer, 400: status.HTTP_400_BAD_REQUEST},
    )
    @action(
        detail=False,
        methods=["get"],
        url_path="get-list-review-about-partner",
        authentication_classes=[AdminJWTAuthentication],
    )
    def get_list_review_about_partner(self, request) -> Response:
        self.request: Request
        queryset = Review.objects.all().select_related(
            "client__current_user", "partner"
        )

        if "search_client" in request.query_params:
            search_result = search_for_client(request.query_params["search_client"])
            queryset = queryset.filter(client__id__in=search_result)

        if "search_partner" in request.query_params:
            search_result = search_for_partner(request.query_params["search_partner"])
            queryset = queryset.filter(partner__id__in=search_result)

        filterset = ReviewFilter(self.request.query_params, queryset=queryset)
        if filterset.is_valid():
            queryset = filterset.qs

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ReviewListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        return Response("", status.HTTP_200_OK)

    @extend_schema(
        summary="Список заказов",
        responses={200: OrderListSerializer, 400: status.HTTP_400_BAD_REQUEST},
    )
    @action(
        detail=False,
        methods=["get"],
        url_path="get-list-orders-for-admin",
        authentication_classes=[AdminJWTAuthentication],
    )
    def get_list_orders_for_admin(self, request) -> Response:
        self.request: Request
        queryset = Order.objects.all().select_related("service", "partner")

        if "search" in request.query_params:
            search_result = search_for_partner(request.query_params["search"])
            queryset = queryset.filter(partner__id__in=search_result)

        filterset = OrderStatusAndServiceFilter(
            self.request.query_params, queryset=queryset
        )
        if filterset.is_valid():
            queryset = filterset.qs

        page = self.paginate_queryset(queryset.order_by("-datetime_created"))
        if page is not None:
            serializer = OrderListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        return Response("", status.HTTP_200_OK)

    @extend_schema(
        summary="Список условий по заказам для админа",
        responses={200: OrderConditionSerializer, 404: status.HTTP_404_NOT_FOUND},
    )
    @action(
        detail=True,
        methods=["get"],
        url_path="get-list-of-order-conditions-by-admin",
        authentication_classes=[AdminJWTAuthentication],
    )
    def get_list_of_order_conditions(self, request, pk=None) -> Response:
        match pk:
            case "radius":
                conditions = OrderConditions.objects.filter(
                    condition_type=OrderConditions.ConditionTypes.radius,
                    option_id__isnull=True,
                ).distinct("title")
            case "fuel_type":
                conditions = OrderConditions.objects.filter(
                    condition_type=OrderConditions.ConditionTypes.fuel_type,
                    option_id__isnull=True,
                ).distinct("title")
            case _:
                raise NotFound
        conditions = conditions.order_by("title")
        serializer = OrderConditionSerializer(conditions, many=True)
        return Response(serializer.data, status.HTTP_200_OK)

    @extend_schema(
        summary="Получить условие по заказам для админа",
        responses={200: OrderConditionSerializer, 404: status.HTTP_404_NOT_FOUND},
    )
    @action(
        detail=True,
        methods=["get"],
        url_path="get-order-condition-by-admin",
        authentication_classes=[AdminJWTAuthentication],
    )
    def get_order_condition(self, request, pk=None) -> Response:
        self.request: Request
        condition = OrderConditions.objects.filter(id=pk).first()
        if condition:
            serializer = OrderConditionSerializer(condition)
            return Response(serializer.data, status.HTTP_200_OK)
        raise NotFound

    @extend_schema(
        summary="Создать условие по заказам для админа",
        request=CreateOrderConditionByAdminSerializer,
        responses={200: OrderConditionSerializer, 400: status.HTTP_400_BAD_REQUEST},
    )
    @action(
        detail=False,
        methods=["post"],
        url_path="create-order-condition-by-admin",
        authentication_classes=[AdminJWTAuthentication],
    )
    def create_order_condition(self, request) -> Response:
        self.request: Request
        serializer = CreateOrderConditionByAdminSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status.HTTP_200_OK)

    @extend_schema(
        summary="Изменить условие по заказам для админа",
        request=CreateOrderConditionByAdminSerializer,
        responses={200: OrderConditionSerializer, 400: status.HTTP_400_BAD_REQUEST},
    )
    @action(
        detail=True,
        methods=["patch"],
        url_path="patch-order-condition-by-admin",
        authentication_classes=[AdminJWTAuthentication],
    )
    def patch_order_condition(self, request, pk=None) -> Response:
        self.request: Request
        condition = get_object_or_404(OrderConditions, pk=pk)
        serializer = CreateOrderConditionByAdminSerializer(
            condition,
            data=self.request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status.HTTP_200_OK)

    @extend_schema(
        summary="Удалить условие по заказам для админа",
        responses={204: status.HTTP_204_NO_CONTENT, 400: status.HTTP_400_BAD_REQUEST},
    )
    @action(
        detail=True,
        methods=["delete"],
        url_path="delete-order-condition-by-admin",
        authentication_classes=[AdminJWTAuthentication],
    )
    def delete_order_condition(self, request, pk=None) -> Response:
        self.request: Request
        condition = OrderConditions.objects.filter(id=pk)
        if condition.exists():
            condition.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        raise NotFound

    @extend_schema(
        summary="Получить список категорий техники для админа",
        responses={200: TechnicCategorySerializer, 404: status.HTTP_404_NOT_FOUND},
    )
    @action(
        detail=False,
        methods=["get"],
        url_path="get-list-of-technic-categories-by-admin",
        authentication_classes=[AdminJWTAuthentication],
    )
    def get_list_of_technic_categories(self, request) -> Response:
        categories = TechnicCategory.objects.all().order_by("-id")
        serializer = TechnicCategorySerializer(categories, many=True)
        return Response(serializer.data, status.HTTP_200_OK)

    @extend_schema(
        summary="Получить категорию техники",
        responses={200: TechnicCategorySerializer, 404: status.HTTP_404_NOT_FOUND},
    )
    @action(
        detail=True,
        methods=["get"],
        url_path="get-technic-category-by-admin",
        authentication_classes=[AdminJWTAuthentication],
    )
    def get_technic_category(self, request, pk=None) -> Response:
        self.request: Request
        category = TechnicCategory.objects.filter(id=pk).first()
        if category:
            serializer = TechnicCategorySerializer(category)
            return Response(serializer.data, status.HTTP_200_OK)
        raise NotFound

    @extend_schema(
        summary="Создать категорию техники для админа",
        request=TechnicCategorySerializer,
        responses={200: TechnicCategorySerializer, 400: status.HTTP_400_BAD_REQUEST},
    )
    @action(
        detail=False,
        methods=["post"],
        url_path="create-technic-category-by-admin",
        authentication_classes=[AdminJWTAuthentication],
    )
    def create_technic_category(self, request) -> Response:
        self.request: Request
        serializer = TechnicCategorySerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status.HTTP_200_OK)

    @extend_schema(
        summary="Измениить категорию техники для админа",
        request=TechnicCategorySerializer,
        responses={200: TechnicCategorySerializer, 400: status.HTTP_400_BAD_REQUEST},
    )
    @action(
        detail=True,
        methods=["patch"],
        url_path="patch-technic-category-by-admin",
        authentication_classes=[AdminJWTAuthentication],
    )
    def patch_technic_category(self, request, pk=None) -> Response:
        self.request: Request
        category = get_object_or_404(TechnicCategory, pk=pk)
        serializer = TechnicCategorySerializer(
            category, data=self.request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status.HTTP_200_OK)

    @extend_schema(
        summary="Удалить категорию техники для админа",
        responses={204: status.HTTP_204_NO_CONTENT, 404: status.HTTP_404_NOT_FOUND},
    )
    @action(
        detail=True,
        methods=["delete"],
        url_path="delete-technic-category-by-admin",
        authentication_classes=[AdminJWTAuthentication],
    )
    def delete_technic_category(self, request, pk=None) -> Response:
        self.request: Request
        category = TechnicCategory.objects.filter(id=pk)
        if category.exists():
            category.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        raise NotFound

    @extend_schema(
        summary="Список городов для админа",
        responses={200: CityListAdminSerializer, 404: status.HTTP_404_NOT_FOUND},
    )
    @action(
        detail=False,
        methods=["get"],
        url_path="cities",
        authentication_classes=[AdminJWTAuthentication],
    )
    def get_list_of_cities_by_admin(self, request):
        self.request: Request
        cities = City.objects.annotate(
            order_count=Count(
                "orders",
                filter=Q(orders__status=Order.OrderStatuses.done),
                distinct=True,
            ),
            partner_count=Count("partners", distinct=True),
            partners_profit_amount=Sum("partners__profit", distinct=True),
        ).prefetch_related("orders", "partners")
        serializer = CityListAdminSerializer(cities, many=True)
        return Response(serializer.data, status.HTTP_200_OK)

    @extend_schema(
        summary="Создать / обновить рабочие зоны с файлом",
        request=TechnicCategorySerializer,
        responses={200: status.HTTP_200_OK, 400: status.HTTP_400_BAD_REQUEST},
    )
    @action(
        detail=False,
        methods=["patch"],
        url_path="working-zones",
        authentication_classes=[AdminJWTAuthentication],
    )
    def create_or_update_working_zones_by_admin(self, request) -> Response:
        self.request: Request
        serializer = WorkingZoneFileUploadSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        file = serializer.validated_data.get("file")
        gj = geojson.load(file)
        update_working_zones(geo_json=gj)
        return Response({"success": True}, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Список рабочих зон",
        request=TechnicCategorySerializer,
        responses={
            200: WorkingZoneReadOnlySerializer,
            400: status.HTTP_400_BAD_REQUEST,
        },
    )
    @action(
        detail=False,
        methods=["get"],
        url_path="get-working-zones",
        authentication_classes=[AdminJWTAuthentication],
    )
    def get_working_zones_by_admin(self, request) -> Response:
        self.request: Request
        busy_param: str = self.request.query_params.get("busy")
        qs = WorkingZone.objects.select_related("city")
        if busy_param and busy_param.lower() == "false":
            qs = qs.filter(city_id__isnull=True)
        serializer = WorkingZoneReadOnlySerializer(qs, many=True)
        return Response(serializer.data, status.HTTP_200_OK)

    @extend_schema(
        summary="Информация об услуге",
        responses={200: status.HTTP_200_OK, 400: status.HTTP_400_BAD_REQUEST},
    )
    @action(
        detail=True,
        methods=["get"],
        url_path="get-service-info",
        authentication_classes=[AdminJWTAuthentication],
    )
    def get_service_info_for_admin(self, request, pk=None):

        partner_count_subquery = (
            PartnerService.objects.filter(service=OuterRef("pk"))
            .values("service")
            .annotate(partner_count=Count("partner", distinct=True))
            .values("partner_count")
        )

        city_count_subquery = (
            PartnerService.objects.filter(service=OuterRef("pk"))
            .values("service")
            .annotate(city_count=Count("partner__city", distinct=True))
            .values("city_count")
        )

        services_with_counts = (
            Service.objects.filter(pk=pk)
            .annotate(
                partners_count=Subquery(partner_count_subquery),
                cities_count=Subquery(city_count_subquery),
            )
            .prefetch_related("options")
            .first()
        )
        serializer = ServiceForAdminSerializer(services_with_counts)
        return Response(serializer.data, status.HTTP_200_OK)

    @extend_schema(
        summary="Деталка опции",
        responses={200: status.HTTP_200_OK, 400: status.HTTP_400_BAD_REQUEST},
    )
    @action(
        detail=True,
        methods=["get"],
        url_path="get-service-option",
        authentication_classes=[AdminJWTAuthentication],
    )
    def get_service_option_for_admin(self, request, pk=None) -> Response:
        self.request: Request
        option = get_object_or_404(Option, pk=pk)
        serializer = OptionSerializer(option)
        return Response(serializer.data, status.HTTP_200_OK)

    @extend_schema(
        summary="Создание опции",
        request=OptionSerializer,
        responses={200: status.HTTP_200_OK, 400: status.HTTP_400_BAD_REQUEST},
    )
    @action(
        detail=False,
        methods=["post"],
        url_path="create-service-options",
        authentication_classes=[AdminJWTAuthentication],
    )
    def create_service_options_for_admin(self, request) -> Response:
        self.request: Request
        serializer = OptionSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Изменение опции",
        request=OptionSerializer,
        responses={200: status.HTTP_200_OK, 400: status.HTTP_400_BAD_REQUEST},
    )
    @action(
        detail=True,
        methods=["patch"],
        url_path="update-service-options",
        authentication_classes=[AdminJWTAuthentication],
    )
    def update_service_options_for_admin(self, request, pk=None) -> Response:
        self.request: Request
        option = get_object_or_404(Option, pk=pk)
        serializer = OptionSerializer(option, data=self.request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status.HTTP_200_OK)

    @extend_schema(
        summary="Удаление опции",
        responses={204: status.HTTP_204_NO_CONTENT, 400: status.HTTP_400_BAD_REQUEST},
    )
    @action(
        detail=True,
        methods=["delete"],
        url_path="delete-service-options",
        authentication_classes=[AdminJWTAuthentication],
    )
    def delete_service_options_for_admin(self, request, pk=None) -> Response:
        self.request: Request
        option = get_object_or_404(Option, pk=pk)
        is_order = Order.objects.filter(options=option).exists()
        if is_order:
            return Response(
                {
                    "success": False,
                    "message": "Опция используется в заказах",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        is_partner_service_option = PartnerServiceOption.objects.filter(
            option=option
        ).exists()
        if is_partner_service_option:
            return Response(
                {
                    "success": False,
                    "message": "Опция используется у партнеров",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        option.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        summary="Получение города",
        responses={200: status.HTTP_200_OK, 400: status.HTTP_400_BAD_REQUEST},
    )
    @action(
        detail=True,
        methods=["get"],
        url_path="get-city",
        authentication_classes=[AdminJWTAuthentication],
    )
    def get_city_for_admin(self, request, pk=None) -> Response:
        self.request: Request
        city = get_object_or_404(City, pk=pk)
        serializer = CityForAdminSerializer(city)
        return Response(serializer.data, status.HTTP_200_OK)

    @extend_schema(
        summary="Создание города",
        request=CityForAdminSerializer,
        responses={200: status.HTTP_200_OK, 400: status.HTTP_400_BAD_REQUEST},
    )
    @action(
        detail=False,
        methods=["post"],
        url_path="create-city",
        authentication_classes=[AdminJWTAuthentication],
    )
    def create_city_for_admin(self, request) -> Response:
        self.request: Request
        serializer = CityForAdminSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status.HTTP_200_OK)

    @extend_schema(
        summary="Изменение города",
        request=CityForAdminSerializer,
        responses={200: status.HTTP_200_OK, 400: status.HTTP_400_BAD_REQUEST},
    )
    @action(
        detail=True,
        methods=["patch"],
        url_path="update-city",
        authentication_classes=[AdminJWTAuthentication],
    )
    def update_city_for_admin(self, request, pk=None) -> Response:
        self.request: Request
        city = get_object_or_404(City, pk=pk)
        serializer = CityForAdminSerializer(city, data=self.request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status.HTTP_200_OK)

    @extend_schema(
        summary="Получение цен",
        responses={200: status.HTTP_200_OK, 400: status.HTTP_400_BAD_REQUEST},
    )
    @action(
        detail=True,
        methods=["get"],
        url_path="get-prices",
        authentication_classes=[AdminJWTAuthentication],
    )
    def get_prices_for_admin(self, request, pk=None) -> Response:
        self.request: Request
        city = get_object_or_404(City, pk=pk)
        services = Service.objects.all()
        serializer = ServiceWithOptionPricesSerializer(
            services,
            many=True,
            context={"city": city},
        )
        return Response(serializer.data, HTTP_200_OK)

    @extend_schema(
        summary="Создание цен",
        request=CreateOptionPriceSerializer,
        responses={200: status.HTTP_200_OK, 400: status.HTTP_400_BAD_REQUEST},
    )
    @action(
        detail=False,
        methods=["post"],
        url_path="create-prices",
        authentication_classes=[AdminJWTAuthentication],
    )
    def create_prices_for_admin(self, request) -> Response:
        self.request: Request
        request_serializer = CreateOptionPriceSerializer(data=self.request.data)
        request_serializer.is_valid(raise_exception=True)
        new_option_price = create_option_price(
            option_id=request_serializer.validated_data.get("option"),
            technic_category_id=request_serializer.validated_data.get(
                "technic_category"
            ),
            city_id=request_serializer.validated_data.get("city"),
            amount=request_serializer.validated_data.get("amount"),
            order_conditions=request_serializer.validated_data.get("order_conditions"),
        )
        response_serializer = OptionPriceSerializer(instance=new_option_price)
        return Response(response_serializer.data, status.HTTP_200_OK)

    @extend_schema(
        summary="Изменение цен",
        request=UpdateOptionPriceSerializer,
        responses={200: status.HTTP_200_OK, 400: status.HTTP_400_BAD_REQUEST},
    )
    @action(
        detail=True,
        methods=["patch"],
        url_path="update-prices",
        authentication_classes=[AdminJWTAuthentication],
    )
    def update_prices_for_admin(self, request, pk=None):
        self.request: Request
        request_serializer = UpdateOptionPriceSerializer(data=self.request.data)
        request_serializer.is_valid(raise_exception=True)
        option_price = update_option_price(
            option_price_id=pk,
            option_id=request_serializer.validated_data.get("option"),
            technic_category_id=request_serializer.validated_data.get(
                "technic_category"
            ),
            city_id=request_serializer.validated_data.get("city"),
            amount=request_serializer.validated_data.get("amount"),
            order_conditions_to_create=request_serializer.validated_data.get(
                "order_conditions_to_create"
            ),
            order_conditions_to_update=request_serializer.validated_data.get(
                "order_conditions_to_update"
            ),
            order_conditions_to_delete=request_serializer.validated_data.get(
                "order_conditions_to_delete"
            ),
        )
        response_serializer = OptionPriceSerializer(instance=option_price)
        return Response(response_serializer.data, status.HTTP_200_OK)

    @extend_schema(
        summary="Удаление цен",
        responses={204: status.HTTP_204_NO_CONTENT, 400: status.HTTP_400_BAD_REQUEST},
    )
    @action(
        detail=True,
        methods=["delete"],
        url_path="delete-prices",
        authentication_classes=[AdminJWTAuthentication],
    )
    def delete_prices_for_admin(self, request, pk=None):
        option_price = get_object_or_404(OptionPrice, pk=pk)
        if option_price:
            option_price.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        summary="Получение заказа",
        responses={200: status.HTTP_200_OK, 400: status.HTTP_400_BAD_REQUEST},
    )
    @action(
        detail=True,
        methods=["get"],
        url_path="get-order",
        authentication_classes=[AdminJWTAuthentication],
    )
    def get_order_for_admin(self, request, pk=None) -> Response:
        self.request: Request
        order = get_object_or_404(Order, pk=pk)
        serializer = CreateOrderForAdminSerializer(order)
        return Response(serializer.data, status.HTTP_200_OK)

    @extend_schema(
        summary="Создание заказа",
        request=CreateOrderForAdminSerializer,
        responses={200: status.HTTP_200_OK, 400: status.HTTP_400_BAD_REQUEST},
    )
    @action(
        detail=False,
        methods=["post"],
        url_path="create-order",
        authentication_classes=[AdminJWTAuthentication],
    )
    def create_order_for_admin(self, request):
        self.request: Request
        serializer = CreateOrderForAdminSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status.HTTP_200_OK)

    @extend_schema(
        summary="Получение списка партнеров для заказа",
        responses={200: status.HTTP_200_OK, 400: status.HTTP_400_BAD_REQUEST},
    )
    @action(
        detail=False,
        methods=["get"],
        url_path="partners-for-order",
        authentication_classes=[AdminJWTAuthentication],
    )
    def get_partner_list_for_order(self, request):
        self.request: Request
        technic_category_id = self.request.query_params.get("technic_category_id", None)
        service_id = self.request.query_params.get("service_id", None)
        city_id = self.request.query_params.get("city_id", None)
        option_ids = self.request.query_params.get("option_ids", [])
        if option_ids:
            option_ids = [
                int(option_id.strip())
                for option_id in self.request.query_params.get("option_ids").split(",")
            ]
        suitable_partner_ids = get_suitable_partner_ids(
            options=option_ids,
            service_id=service_id,
            city_id=city_id,
            technic_category_id=technic_category_id,
        )
        serializer = PartnerSimplePhoneAndPhotoSerializer(
            Partner.objects.filter(id__in=suitable_partner_ids).select_related(
                "current_user"
            ),
            many=True,
        )
        return Response(serializer.data, status.HTTP_200_OK)

    @extend_schema(
        summary="Изменение заказа",
        request=CreateOrderForAdminSerializer,
        responses={
            200: status.HTTP_200_OK,
            400: status.HTTP_400_BAD_REQUEST,
            404: status.HTTP_404_NOT_FOUND,
        },
    )
    @action(
        detail=True,
        methods=["patch"],
        url_path="update-order",
        authentication_classes=[AdminJWTAuthentication],
    )
    def update_order_for_admin(self, request, pk=None) -> Response:
        self.request: Request
        with transaction.atomic():
            order = Order.objects.select_for_update().filter(pk=pk).first()
            if order:
                serializer = CreateOrderForAdminSerializer(
                    order,
                    data=self.request.data,
                    partial=True,
                )
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response(serializer.data, status.HTTP_200_OK)
            raise NotFound

    @extend_schema(
        summary="Отмена заказа",
        responses={
            200: status.HTTP_200_OK,
            400: status.HTTP_400_BAD_REQUEST,
            404: status.HTTP_404_NOT_FOUND,
        },
    )
    @action(
        detail=True,
        methods=["patch"],
        url_path="cancel-order",
        authentication_classes=[AdminJWTAuthentication],
    )
    def cancel_order_for_admin(self, request, pk=None) -> Response:
        self.request: Request
        with transaction.atomic():
            order = Order.objects.select_for_update().filter(pk=pk).first()
            if order:
                order.status = Order.OrderStatuses.cancelled
                order.save()
                return Response(status.HTTP_200_OK)
            raise NotFound

    @extend_schema(
        summary="Изменить статус заказа",
        responses={
            200: status.HTTP_200_OK,
            400: status.HTTP_400_BAD_REQUEST,
            404: status.HTTP_404_NOT_FOUND,
            409: status.HTTP_409_CONFLICT,
        },
    )
    @action(
        detail=True,
        methods=["patch"],
        url_path="change-order-status",
        authentication_classes=[AdminJWTAuthentication],
    )
    def change_order_status_for_admin(self, request, pk=None) -> Response:
        self.request: Request
        serializer = ChangeOrderStatusSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            order = Order.objects.select_for_update().filter(pk=pk).first()
            if order:
                new_status = serializer.validated_data.get("status")
                if new_status not in (
                    Order.OrderStatuses.done,
                    Order.OrderStatuses.cancelled,
                ):
                    raise ValidationError
                if order.status == Order.OrderStatuses.on_confirmation:
                    order.status = new_status
                    order.save()
                else:
                    return Response(status.HTTP_409_CONFLICT)
                return Response(status.HTTP_200_OK)
            raise NotFound

    @extend_schema(
        summary="Создание минимального депозита",
        request=CreateDepositAndCommissionSerializer,
        responses={
            200: status.HTTP_200_OK,
            400: status.HTTP_400_BAD_REQUEST,
        },
    )
    @action(
        detail=False,
        methods=["post"],
        url_path="create_deposit_commission",
        authentication_classes=[AdminJWTAuthentication],
    )
    def create_deposit_minimum(
        self,
        request: Request,
    ) -> Response:
        self.request: Request
        serializer = CreateDepositAndCommissionSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        deposit_minimum = DepositMinimum.objects.first()
        if deposit_minimum:
            deposit_minimum.amount = serializer.validated_data["deposit_minimum"]
            deposit_minimum.save()
        else:
            DepositMinimum.objects.create(
                amount=serializer.validated_data["deposit_minimum"],
            )
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
        )

    @extend_schema(
        summary="Получение минимального депозита",
        responses={
            200: status.HTTP_200_OK,
            400: status.HTTP_400_BAD_REQUEST,
        },
    )
    @action(
        detail=False,
        methods=["get"],
        url_path="get_deposit_commission",
        authentication_classes=[AdminJWTAuthentication],
    )
    def get_deposit_minimum(self, request: Request):
        deposit_minimum_obj = DepositMinimum.objects.first()
        deposit_minimum = deposit_minimum_obj.amount if deposit_minimum_obj else None
        return Response(
            {
                "deposit_minimum": deposit_minimum,
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        summary="Создать / изменить версии устройств",
        responses={
            201: status.HTTP_201_CREATED,
            400: status.HTTP_400_BAD_REQUEST,
        },
    )
    @action(
        detail=False,
        methods=["post"],
        url_path="create-app-versions",
        authentication_classes=[AdminJWTAuthentication],
    )
    def create_update_app_versions(self, request: Request) -> Response:

        app_version: MobileAppVersion = MobileAppVersion.objects.first()
        serializer = MobileAppVersionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if app_version:
            app_version.ios_partner = serializer.validated_data.get("ios_partner")
            app_version.android_partner = serializer.validated_data.get(
                "android_partner"
            )
            app_version.ios_client = serializer.validated_data.get("ios_client")
            app_version.android_client = serializer.validated_data.get("android_client")
            app_version.save()
        else:
            MobileAppVersion.objects.create(
                ios_partner=serializer.validated_data.get("ios_partner"),
                android_partner=serializer.validated_data.get("android_partner"),
                ios_client=serializer.validated_data.get("ios_client"),
                android_client=serializer.validated_data.get("android_client"),
            )

        return Response(serializer.data, status.HTTP_201_CREATED)

    @extend_schema(
        summary="Создать марки и модели",
        request=CreateCarBrandSerializer,
        responses={
            201: status.HTTP_201_CREATED,
            400: status.HTTP_400_BAD_REQUEST,
        },
    )
    @action(
        detail=False,
        methods=["post"],
        url_path="create-technic",
        authentication_classes=[AdminJWTAuthentication],
    )
    def create_technic(self, request: Request) -> Response:
        request_serializer = CreateCarBrandSerializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)
        new_brand = create_car_brand(
            title=request_serializer.validated_data.get("title"),
            cyrillic_title=request_serializer.validated_data.get("cyrillic_title"),
            models=request_serializer.validated_data.get("models"),
        )
        return Response({"id": new_brand.id}, status.HTTP_201_CREATED)

    @extend_schema(
        summary="Изменить марки и модели",
        request=UpdateCarBrandSerializer,
        responses={
            200: status.HTTP_200_OK,
            400: status.HTTP_400_BAD_REQUEST,
        },
    )
    @action(
        detail=True,
        methods=["patch"],
        url_path="update-technic",
        authentication_classes=[AdminJWTAuthentication],
    )
    def update_technic(
        self,
        request: Request,
        pk=None,
    ) -> Response:
        request_serializer = UpdateCarBrandSerializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)
        update_car_brand(
            car_brand_id=pk,
            title=request_serializer.validated_data.get("title"),
            cyrillic_title=request_serializer.validated_data.get("cyrillic_title"),
            models_to_create=request_serializer.validated_data.get("models_to_create"),
            models_to_update=request_serializer.validated_data.get("models_to_update"),
            models_to_delete=request_serializer.validated_data.get("models_to_delete"),
        )
        return Response(status=status.HTTP_200_OK)

    @extend_schema(
        summary="Деталка марок и моделей",
        responses={
            201: status.HTTP_201_CREATED,
            400: status.HTTP_400_BAD_REQUEST,
        },
    )
    @action(
        detail=True,
        methods=["get"],
        url_path="get-technic",
        authentication_classes=[AdminJWTAuthentication],
    )
    def get_technic(self, request: Request, pk=None) -> Response:
        brand = (
            CarBrandList.objects.filter(id=pk)
            .prefetch_related("models")
            .order_by("title")
        ).first()
        if not brand:
            raise NotFound
        serializer = CarBrandListSerializer(brand)
        return Response(serializer.data, status.HTTP_200_OK)

    @extend_schema(
        summary="Удаление марок и моделей",
        responses={204: status.HTTP_204_NO_CONTENT},
    )
    @action(
        detail=True,
        methods=["delete"],
        url_path="delete-technic",
        authentication_classes=[AdminJWTAuthentication],
    )
    def delete_technic(self, request: Request, pk=None) -> Response:
        CarBrandList.objects.filter(id=pk).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        summary="Расчет комиссии партнера",
        request=CalculateCommissionRequestSerializer,
        responses={200: CommissionResponseSerializer},
    )
    @action(
        detail=False,
        methods=["post"],
        url_path="calculate-partner-commission",
        authentication_classes=[AdminJWTAuthentication],
    )
    def calculate_partner_commission(self, request: Request) -> Response:
        self.request: Request

        serializer = CalculateCommissionRequestSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data
        date_from = validated_data["date_from"]
        date_to = validated_data["date_to"]
        partner_id = validated_data["partner_id"]

        partner = get_object_or_404(Partner, pk=partner_id)

        result = calculate_partner_commission(
            partner_id=partner.id,
            date_from=date_from,
            date_to=date_to,
        )

        response_data = {
            "total_commission": result["total_commission"],
            "orders_count": result["orders_count"],
            "period": {
                "from": date_from.isoformat(),
                "to": date_to.isoformat(),
            },
            "orders": result["orders"],
        }

        return Response(response_data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Расчет общих комиссий сервиса",
        request=CalculateCommissionRequestSerializer,
        responses={200: ServiceCommissionResponseSerializer},
    )
    @action(
        detail=False,
        methods=["post"],
        url_path="calculate-service-commissions",
        authentication_classes=[AdminJWTAuthentication],
    )
    def calculate_service_commissions(self, request: Request) -> Response:
        self.request: Request
        serializer = CalculateCommissionRequestSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data
        date_from = validated_data["date_from"]
        date_to = validated_data["date_to"]

        result = calculate_service_commissions(
            date_from=date_from,
            date_to=date_to,
        )

        response_data = {
            "total_commission": result["total_commission"],
            "orders_count": result["orders_count"],
            "period": {
                "from": date_from.isoformat(),
                "to": date_to.isoformat(),
            },
        }

        return Response(response_data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Получить историю сообщений чата между клиентом и исполнителем",
        parameters=[
            OpenApiParameter(
                name="order_id",
                type=int,
                location=OpenApiParameter.QUERY,
                required=True,
                description="ID заказа для получения истории чата",
            ),
        ],
        responses={
            200: inline_serializer(
                name="ChatHistoryResponse",
                fields={
                    "order_id": serializers.IntegerField(),
                    "total_count": serializers.IntegerField(),
                    "messages": MessageSerializer(many=True),
                },
            ),
            400: status.HTTP_400_BAD_REQUEST,
            404: status.HTTP_404_NOT_FOUND,
        },
    )
    @action(
        detail=False,
        methods=["get"],
        url_path="chat/get-history",
        authentication_classes=[AdminJWTAuthentication],
    )
    def get_chat_history(self, request: Request) -> Response:
        order_param = request.query_params.get("order_id")
        if not order_param:
            return Response(
                {"error": "order_id is required"}, status=status.HTTP_400_BAD_REQUEST
            )
        order_id = int(order_param)

        if not order_id:
            return Response(
                {"error": "Параметр order_id обязателен"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            history_data = get_chat_history(order_id=order_id)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)

        serializer = MessageSerializer(history_data["messages"], many=True)

        return Response(
            {
                "order_id": history_data["order_id"],
                "total_count": history_data["total_count"],
                "messages": list(reversed(serializer.data)),
            },
            status=status.HTTP_200_OK,
        )
