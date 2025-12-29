from django.core.exceptions import ValidationError
from rest_framework import serializers, exceptions
from rest_framework.response import Response
from rest_framework.views import exception_handler


def custom_error(
    text_error: str, status_code_error: int = 400
) -> exceptions.ValidationError:
    """
    add serializers validation error status code
    """
    error = serializers.ValidationError(text_error)
    error.status_code = status_code_error
    return error


def handle_django_validation_error(exc, context):
    """Handle django core's errors."""
    response = exception_handler(exc, context)
    if response is None and isinstance(exc, ValidationError):
        return Response(status=400, data=exc.message_dict)
    return response
