from rest_framework import serializers
from django.conf import settings
from django.contrib.auth.hashers import make_password
from .models import Usuario
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class UserSerializer(serializers.ModelSerializer):
    """
    Serializador para mostrar la información de un usuario.
    No expone campos sensibles como la contraseña.
    """
    class Meta:
        model = Usuario
        fields = ('id', 'username', 'first_name', 'last_name', 'rol', 'is_active')
        read_only_fields = fields


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        # Usamos el nuevo UserSerializer para asegurar consistencia
        # y devolver todos los atributos del usuario.
        data['usuario'] = UserSerializer(self.user).data
        return data


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    rol = serializers.ChoiceField(choices=Usuario.Rol.choices, default=Usuario.Rol.EMPLEADO)

    class Meta:
        model = Usuario
        fields = ('username', 'password', 'first_name', 'last_name', 'rol')

    def validate_username(self, value):
        if Usuario.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("Ya existe un usuario con este nombre.")
        return value

    def create(self, validated_data):
        # El rol es especificado por el admin, con 'EMPLEADO' como default.
        user = Usuario.objects.create(
            username=validated_data['username'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            rol=validated_data['rol'],
            password=make_password(validated_data['password'])
        )
        return user


class LoginInvitadoSerializer(serializers.Serializer):
    nombre = serializers.CharField()
    codigo_admin = serializers.CharField(write_only=True)

    def validate(self, datos):
        if datos["codigo_admin"] != settings.CODIGO_ADMIN_INVITADO:
            raise serializers.ValidationError("Código de administrador inválido")

        return datos
