from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from django.contrib.auth.hashers import make_password
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import Usuario
from .serializers import LoginInvitadoSerializer, UserRegistrationSerializer, MyTokenObtainPairSerializer, UserSerializer
from apps.core.permissions import IsAdminUser
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator


class MyTokenObtainPairView(TokenObtainPairView):
    """
    Vista de login personalizada para devolver datos del usuario junto con los tokens.
    """
    serializer_class = MyTokenObtainPairSerializer

@method_decorator(csrf_exempt, name="dispatch")
class UserRegistrationAPIView(APIView):
    """
    Vista para que un administrador registre nuevos usuarios (empleados/admins).
    """
    permission_classes = [IsAuthenticated, IsAdminUser]
    serializer_class = UserRegistrationSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        # serializer.save() devuelve la instancia del usuario creado
        usuario = serializer.save()
        # Devolvemos los datos del usuario recién creado
        return Response(
            UserSerializer(usuario).data,
            status=status.HTTP_201_CREATED
        )

@method_decorator(csrf_exempt, name="dispatch")
class VistaLoginInvitado(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginInvitadoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        nombre = serializer.validated_data["nombre"]

        # Creamos un nombre de usuario único para evitar colisiones
        username = f"invitado_{nombre.lower().replace(' ', '_')}_{Usuario.objects.count()}"

        usuario = Usuario.objects.create(
            username=username,
            first_name=nombre,
            rol=Usuario.Rol.INVITADO,
            password=make_password(None),  # Los invitados no tienen contraseña para iniciar sesión
        )

        # Generamos tokens JWT para el nuevo usuario invitado
        refresh = RefreshToken.for_user(usuario)

        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            # Usamos el nuevo UserSerializer para asegurar consistencia
            "usuario": UserSerializer(usuario).data
        })


class LogoutAPIView(APIView):
    """
    Vista para invalidar el refresh token del usuario (logout).
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()

            # HTTP 205 Reset Content: El servidor ha cumplido la solicitud 
            # y no necesita devolver un contenido.
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except TokenError:
            return Response({"error": "Token inválido o expirado"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
