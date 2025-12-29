from rest_framework import serializers

from src.models.simple_models import QuestionAnswer


class QuestionAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionAnswer
        fields = ["id", "question", "answer", "questioner"]
