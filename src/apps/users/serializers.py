from rest_framework import serializers
from django.conf import settings
from django.contrib.auth.hashers import make_password
from rest_framework.exceptions import AuthenticationFailed
from .models import Usuario
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class UserSerializer(serializers.ModelSerializer):
    """
    Serializador de solo lectura para mostrar la información de un usuario.
    Diseñado para ser seguro, no expone campos sensibles como la contraseña.
    """
    class Meta:
        model = Usuario
        fields = ('id', 'username', 'first_name', 'last_name', 'rol', 'is_active')
        read_only_fields = fields


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Personaliza el serializador de login de JWT para incluir los datos completos
    del usuario en la respuesta, además de los tokens de acceso y refresco.
    """
    def validate(self, attrs):
        # Llama al método padre para obtener los tokens.
        # El método padre ya establece self.user si las credenciales son válidas.
        data = super().validate(attrs)
        # Regla: Un usuario debe estar activo para poder iniciar sesión.
        if not self.user.activo:
            raise AuthenticationFailed("Usuario inactivo. Contacte al administrador.")
        # Usamos el UserSerializer para asegurar consistencia
        # y devolver todos los atributos del usuario de forma segura.
        data['usuario'] = UserSerializer(self.user).data
        return data


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializador de escritura para registrar nuevos usuarios (empleados o administradores).
    Maneja la validación de datos y el hasheo de la contraseña.
    """
    # `write_only=True` asegura que la contraseña no se incluya en la respuesta.
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    rol = serializers.ChoiceField(choices=Usuario.Rol.choices, default=Usuario.Rol.EMPLEADO)

    class Meta:
        model = Usuario
        fields = ('username', 'password', 'first_name', 'last_name', 'rol')

    def validate_username(self, value):
        """Valida que el nombre de usuario sea único (insensible a mayúsculas/minúsculas)."""
        if Usuario.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("Ya existe un usuario con ese nombre.")
        return value

    def create(self, validated_data):
        """
        Crea una nueva instancia de Usuario.
        El rol es especificado por el admin, con 'EMPLEADO' como default.
        La contraseña se hashea antes de guardarse.
        """
        user = Usuario.objects.create(
            username=validated_data['username'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            rol=validated_data['rol'],
            # `make_password` es la forma segura de hashear la contraseña.
            password=make_password(validated_data['password'])
        )
        return user


class LoginInvitadoSerializer(serializers.Serializer):
    """
    Serializador de escritura para validar los datos de entrada del login de invitado.
    """
    nombre = serializers.CharField()
    codigo_admin = serializers.CharField(write_only=True)

    def validate(self, datos):
        """Valida que el código de administrador sea correcto."""
        if datos["codigo_admin"] != settings.CODIGO_ADMIN_INVITADO:
            raise serializers.ValidationError("Código de administrador inválido")

        return datos
