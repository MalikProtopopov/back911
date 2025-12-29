from rest_framework import routers

from src.views.contacts_view import ContactsViewSet

contacts_router = routers.SimpleRouter()
contacts_router.register(r"", ContactsViewSet)
