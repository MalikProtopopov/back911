from rest_framework import routers

from src.views.question_answer_view import QuestionAnswerViewSet

question_answer_router = routers.SimpleRouter()
question_answer_router.register(r"", QuestionAnswerViewSet)
