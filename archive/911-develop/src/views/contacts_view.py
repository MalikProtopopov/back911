from drf_spectacular.utils import extend_schema
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from src.models.simple_models import Contacts
from src.serializers.contacts_serializer import ContactsSerializer


class ContactsViewSet(viewsets.ViewSet):
    queryset = Contacts.objects.all()
    serializer_class = ContactsSerializer

    @extend_schema(
        summary="Получить контакты",
        responses={200: status.HTTP_200_OK, 404: status.HTTP_404_NOT_FOUND},
    )
    @action(detail=False, methods=["get"], url_path="get-contacts")
    def get_contacts(self, request):
        contacts = Contacts.objects.first()
        if contacts:
            serializer = ContactsSerializer(contacts)
            return Response(serializer.data, status.HTTP_200_OK)
        return Response("", status.HTTP_200_OK)
