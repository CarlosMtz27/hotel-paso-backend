from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.conf import settings

from .models import Usuario


class UserAuthAPITests(APITestCase):
    def setUp(self):
        # --- Users ---
        self.admin_user = Usuario.objects.create_user(username='admin', password='password123', rol=Usuario.Rol.ADMINISTRADOR)
        self.employee_user = Usuario.objects.create_user(username='employee', password='password123', rol=Usuario.Rol.EMPLEADO)

        # --- URLs ---
        self.register_url = reverse('register')
        self.login_invitado_url = reverse('login_invitado')
        self.login_url = reverse('token_obtain_pair') # Asumiendo que esta es la URL de login JWT
        self.logout_url = reverse('logout')

    def test_admin_puede_registrar_usuario(self):
        """Verifica que un administrador puede registrar un nuevo empleado."""
        self.client.force_authenticate(user=self.admin_user)
        data = {
            "username": "nuevo_empleado",
            "password": "password_segura",
            "first_name": "Nuevo",
            "last_name": "Empleado",
            "rol": "EMPLEADO"
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Usuario.objects.count(), 3)
        self.assertEqual(response.data['username'], 'nuevo_empleado')

    def test_empleado_no_puede_registrar_usuario(self):
        """Verifica que un empleado no tiene permisos para registrar nuevos usuarios."""
        self.client.force_authenticate(user=self.employee_user)
        data = {"username": "otro_empleado", "password": "password123"}
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_login_invitado_exitoso(self):
        """Verifica que el login de invitado funciona con el código de administrador correcto."""
        data = {
            "nombre": "Juan Perez",
            "codigo_admin": settings.CODIGO_ADMIN_INVITADO
        }
        response = self.client.post(self.login_invitado_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertEqual(response.data['usuario']['rol'], 'INVITADO')
        self.assertEqual(response.data['usuario']['first_name'], 'Juan Perez')

    def test_login_invitado_falla_codigo_incorrecto(self):
        """Verifica que el login de invitado falla si el código de administrador es incorrecto."""
        data = {
            "nombre": "Ana Gomez",
            "codigo_admin": "codigo_incorrecto"
        }
        response = self.client.post(self.login_invitado_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Código de administrador inválido", str(response.data))

    def test_logout_invalida_refresh_token(self):
        """Verifica que el endpoint de logout invalida el refresh token (lo añade a la lista negra)."""
        # 1. Iniciar sesión para obtener tokens
        login_data = {"username": "employee", "password": "password123"}
        login_response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        access_token = login_response.data['access']
        refresh_token = login_response.data['refresh']

        # 2. Hacer logout con el refresh token
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        logout_data = {"refresh": refresh_token}
        logout_response = self.client.post(self.logout_url, logout_data, format='json')
        self.assertEqual(logout_response.status_code, status.HTTP_205_RESET_CONTENT)

        # 3. Intentar usar el refresh token invalidado para obtener un nuevo access token (debería fallar con 401)
        refresh_view_url = reverse('token_refresh')
        refresh_response = self.client.post(refresh_view_url, logout_data, format='json')
        self.assertEqual(refresh_response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('token_not_valid', refresh_response.data['code'])

    def test_registro_usuario_duplicado_falla(self):
        """Verifica que la API no permite registrar un usuario con un username que ya existe."""
        self.client.force_authenticate(user=self.admin_user)
        data = {
            "username": "employee",  # Este usuario ya existe
            "password": "password_nueva",
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Ya existe un usuario con ese nombre.", str(response.data['username']))

    def test_usuario_inactivo_no_puede_iniciar_sesion(self):
        """Verifica que un usuario con `activo=False` no puede obtener un token de acceso."""
        self.employee_user.activo = False
        self.employee_user.save()
        login_data = {"username": "employee", "password": "password123"}
        response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
