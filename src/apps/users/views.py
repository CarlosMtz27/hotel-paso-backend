from rest_framework.response import Response
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import LoginInvitadoSerializer, UserRegistrationSerializer, MyTokenObtainPairSerializer, UserSerializer
from apps.core.permissions import IsAdminUser
from .services import login_invitado_service


class MyTokenObtainPairView(TokenObtainPairView):
    """
    Vista de login personalizada para devolver datos del usuario junto con los tokens.
    Hereda de la vista de JWT y especifica nuestro serializador personalizado.
    """
    serializer_class = MyTokenObtainPairSerializer

class UserRegistrationAPIView(generics.CreateAPIView):
    """
    Vista para que un administrador registre nuevos usuarios (empleados/admins).
    Solo accesible por administradores autenticados.
    Usa una vista genérica para simplificar el código de creación.
    """
    permission_classes = [IsAuthenticated, IsAdminUser]
    serializer_class = UserRegistrationSerializer

    def create(self, request, *args, **kwargs):
        # Sobrescribimos `create` para usar nuestro UserSerializer en la respuesta.
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(UserSerializer(serializer.instance).data, status=status.HTTP_201_CREATED)

class VistaLoginInvitado(generics.GenericAPIView):
    """
    Vista para el login de invitados. No requiere autenticación previa.
    Crea un usuario temporal de tipo 'INVITADO' y le genera tokens JWT.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Maneja la petición POST para el login de invitado.
        1. Valida el nombre y el código de administrador.
        2. Crea un usuario 'INVITADO' temporal.
        3. Genera y devuelve tokens JWT para este usuario.
        """
        serializer = LoginInvitadoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Delegamos la lógica de creación y generación de tokens a la capa de servicios.
        usuario, tokens = login_invitado_service(nombre=serializer.validated_data["nombre"])

        return Response({
            "refresh": tokens["refresh"],
            "access": tokens["access"],
            # Usamos el UserSerializer para asegurar consistencia y seguridad en la respuesta.
            "usuario": UserSerializer(usuario).data
        })


class LogoutAPIView(APIView):
    """
    Vista para invalidar el refresh token del usuario (logout).
    Requiere que el usuario esté autenticado.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Maneja la petición POST para el logout.
        Añade el refresh token a la lista negra para que no pueda ser reutilizado.
        """
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()

            # HTTP 205 Reset Content: El servidor ha cumplido la solicitud
            # y no necesita devolver un contenido. Es una respuesta adecuada para logout.
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except (TokenError, KeyError):
            # Capturamos TokenError si el token es inválido, y KeyError si "refresh" no está en el body.
            return Response({"error": "Token de refresco inválido o no proporcionado."}, status=status.HTTP_400_BAD_REQUEST)


class CurrentUserAPIView(APIView):
    """
    Vista para obtener los datos del usuario actualmente autenticado.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Devuelve los datos del usuario que realiza la petición.
        """
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
