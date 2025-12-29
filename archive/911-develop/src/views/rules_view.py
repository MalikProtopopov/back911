from drf_spectacular.utils import extend_schema
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from src.models.simple_models import Rules
from src.serializers.rules_serializer import RulesSerializer


class RulesViewSet(viewsets.ViewSet):
    queryset = Rules.objects.all()
    serializer_class = RulesSerializer

    @extend_schema(
        summary="Правила пользования",
        responses={200: status.HTTP_200_OK, 404: status.HTTP_404_NOT_FOUND},
    )
    @action(
        detail=False,
        methods=["get"],
        url_path="get-rules",
    )
    def get_rules(self, request):
        rules = Rules.objects.first()
        if rules:
            serializer = RulesSerializer(rules)
            return Response(serializer.data, status.HTTP_200_OK)
        return Response("", status.HTTP_200_OK)
