from django.db.models import Q
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from config.jwt_auth import PartnerJWTAuthentication
from src.models.simple_models import QuestionAnswer
from src.serializers.question_answer_serializer import QuestionAnswerSerializer


class QuestionAnswerViewSet(viewsets.ViewSet):
    queryset = QuestionAnswer.objects.all()
    serializer_class = QuestionAnswerSerializer

    @extend_schema(
        summary="Вопросы / ответы для клиентов", responses={200: status.HTTP_200_OK}
    )
    @action(detail=False, methods=["get"], url_path="client-questions")
    def get_client_questions(self, request) -> Response:
        client_queryset = self.queryset.filter(Q(questioner="client"))
        serializer = self.serializer_class(client_queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Вопросы / ответы для партнеров", responses={200: status.HTTP_200_OK}
    )
    @action(
        detail=False,
        methods=["get"],
        url_path="partner-questions",
        permission_classes=[
            IsAuthenticated,
        ],
        authentication_classes=[PartnerJWTAuthentication],
    )
    def get_partner_questions(self, request) -> Response:
        partner_queryset = self.queryset.filter(Q(questioner="partner"))
        serializer = self.serializer_class(partner_queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
