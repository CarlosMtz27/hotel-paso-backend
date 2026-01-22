from django.contrib.auth import authenticate
from rest_framework import serializers
from django.conf import settings

class LoginSerializer(serializers.Serializer):
    usuario = serializers.CharField()
    contrasena = serializers.CharField(write_only = True)

    def validate(self,datos):
        usuario = authenticate(
            username = datos["usuario"],
            password = datos["contrasena"],
        )

        if not usuario:
            raise serializers.ValidationError("Credenciales inválidas")

        if not usuario.activo:
            raise serializers.ValidationError("Usuario inactivo")

        datos["usuario_autenticado"] = usuario
        return datos


class LoginInvitadoSerializer(serializers.Serializer):
    nombre = serializers.CharField()
    codigo_admin = serializers.CharField(write_only=True)

    def validate(self, datos):
        if datos["codigo_admin"] != settings.CODIGO_ADMIN_INVITADO:
            raise serializers.ValidationError("Código de administrador inválido")

        return datos
