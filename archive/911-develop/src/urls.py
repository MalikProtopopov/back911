from django.urls import include, path

from src.routers.admin_router import admin_router
from src.routers.balance_router import balance_router
from src.routers.client_router import client_router
from src.routers.contacts_router import contacts_router
from src.routers.fcmtoken_router import fcmtoken_router
from src.routers.init_router import init_router
from src.routers.partner_router import partner_router
from src.routers.question_answer_router import question_answer_router
from src.routers.rules_router import rules_router
from src.routers.utils_router import utils_router

urlpatterns = [
    path("client/", include(client_router.urls)),
    path("partner/", include(partner_router.urls)),
    path("utils/", include(utils_router.urls)),
    path("question-answer/", include(question_answer_router.urls)),
    path("admin/", include(admin_router.urls)),
    path("contacts/", include(contacts_router.urls)),
    path("rules/", include(rules_router.urls)),
    path("fcmtoken/", include(fcmtoken_router.urls)),
    path("init/", include(init_router.urls)),
    path("balance/", include(balance_router.urls)),
]
