from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.contrib.auth import login
from django.contrib.auth.hashers import make_password
from .models import Usuario
from .serializers import LoginInvitadoSerializer, LoginSerializer



class VistaLogin(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({
            "mensaje": "Usa POST para iniciar sesión",
            "campos": {
                "usuario": "string",
                "contrasena": "string"
            }
        })

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        usuario = serializer.validated_data["usuario_autenticado"]
        login(request, usuario)

        return Response({
            "id": usuario.id,
            "usuario": usuario.username,
            "rol": usuario.rol,
        })


class VistaLoginInvitado(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginInvitadoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        nombre = serializer.validated_data["nombre"]

        usuario = Usuario.objects.create(
            username=f"invitado_{nombre.lower()}",
            first_name=nombre,
            rol=Usuario.Rol.INVITADO,
            password=make_password(None),
        )

        login(request, usuario)

        return Response({
            "usuario": usuario.username,
            "rol": usuario.rol,
            "mensaje": "Invitado autenticado"
        })
