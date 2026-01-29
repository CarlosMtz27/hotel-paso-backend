from django.db import IntegrityError
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


def custom_exception_handler(exc, context):
    """
    Manejador de excepciones personalizado para la API.
    - Captura `IntegrityError` de la base de datos (causado por `on_delete=PROTECT`).
    - Lo convierte en una respuesta `409 Conflict` con un mensaje claro.
    """
    # Primero, deja que DRF maneje la excepción por defecto.
    response = exception_handler(exc, context)

    # Si la excepción es un IntegrityError y DRF no la manejó, nosotros lo hacemos.
    if response is None and isinstance(exc, IntegrityError):
        return Response(
            {"error": "No se puede eliminar este objeto porque está siendo utilizado por otros registros."},
            status=status.HTTP_409_CONFLICT
        )

    return response