from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.core.exceptions import ValidationError

from apps.users.models import Usuario
from .models import TipoHabitacion
from .services import crear_tipo_habitacion, actualizar_tipo_habitacion


class TipoHabitacionServiceTests(APITestCase):
    def test_crear_tipo_habitacion_exitoso(self):
        """Prueba que el servicio crea un tipo de habitación correctamente."""
        tipo = crear_tipo_habitacion(nombre="Sencilla", descripcion="Habitación para una persona")
        self.assertEqual(TipoHabitacion.objects.count(), 1)
        self.assertEqual(tipo.nombre, "Sencilla")

    def test_crear_tipo_habitacion_duplicado_falla(self):
        """Prueba que el servicio no permite crear tipos con el mismo nombre."""
        crear_tipo_habitacion(nombre="Doble")
        with self.assertRaisesMessage(ValidationError, "Ya existe un tipo de habitación con ese nombre"):
            crear_tipo_habitacion(nombre="Doble")


class TipoHabitacionAPITests(APITestCase):
    def setUp(self):
        # Crear usuarios con diferentes roles
        self.admin_user = Usuario.objects.create_user(username='admin', password='password123', rol=Usuario.Rol.ADMINISTRADOR)
        self.employee_user = Usuario.objects.create_user(username='employee', password='password123', rol=Usuario.Rol.EMPLEADO)

        # Crear un tipo de habitación de prueba
        self.tipo_habitacion = crear_tipo_habitacion(nombre="Suite Presidencial")

        # URLs
        self.list_create_url = reverse('tipos_list')
        self.detail_url = reverse('tipos_detail', kwargs={'pk': self.tipo_habitacion.pk})

    def test_empleado_puede_listar_tipos(self):
        """Prueba que un usuario autenticado (empleado) puede listar los tipos."""
        self.client.force_authenticate(user=self.employee_user)
        response = self.client.get(self.list_create_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_admin_puede_crear_tipo(self):
        """Prueba que un administrador puede crear un tipo de habitación."""
        self.client.force_authenticate(user=self.admin_user)
        data = {'nombre': 'Matrimonial', 'descripcion': 'Cama Queen Size'}
        response = self.client.post(self.list_create_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(TipoHabitacion.objects.count(), 2)

    def test_empleado_no_puede_crear_tipo(self):
        """Prueba que un empleado no puede crear un tipo de habitación."""
        self.client.force_authenticate(user=self.employee_user)
        data = {'nombre': 'Familiar'}
        response = self.client.post(self.list_create_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_puede_actualizar_tipo(self):
        """Prueba que un administrador puede actualizar un tipo de habitación."""
        self.client.force_authenticate(user=self.admin_user)
        data = {'nombre': 'Suite de Lujo', 'activo': False}
        response = self.client.put(self.detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.tipo_habitacion.refresh_from_db()
        self.assertEqual(self.tipo_habitacion.nombre, 'Suite de Lujo')
        self.assertFalse(self.tipo_habitacion.activo)

    def test_empleado_no_puede_actualizar_tipo(self):
        """Prueba que un empleado no puede actualizar un tipo de habitación."""
        self.client.force_authenticate(user=self.employee_user)
        data = {'nombre': 'Suite de Lujo'}
        response = self.client.put(self.detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
