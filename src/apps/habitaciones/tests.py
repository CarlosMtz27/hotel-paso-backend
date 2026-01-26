from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.users.models import Usuario
from .models import TipoHabitacion, Habitacion


class TipoHabitacionAPITests(APITestCase):
    def setUp(self):
        # Crear usuarios con diferentes roles
        self.admin_user = Usuario.objects.create_user(username='admin', password='password123', rol=Usuario.Rol.ADMINISTRADOR)
        self.employee_user = Usuario.objects.create_user(username='employee', password='password123', rol=Usuario.Rol.EMPLEADO)

        # Crear un tipo de habitación de prueba
        self.tipo_habitacion = TipoHabitacion.objects.create(nombre="Suite Presidencial")

        # URLs
        self.list_create_url = reverse('tipos_list')
        self.detail_url = reverse('tipos_detail', kwargs={'pk': self.tipo_habitacion.pk})

    def test_empleado_puede_listar_tipos(self):
        """Prueba que un usuario autenticado (empleado) puede listar los tipos."""
        self.client.force_authenticate(user=self.employee_user)
        response = self.client.get(self.list_create_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Handle paginated and non-paginated responses
        results = response.data.get('results', response.data)
        self.assertEqual(len(results), 1)

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

    def test_crear_tipo_duplicado_falla_api(self):
        """Prueba que la API no permite crear tipos con el mismo nombre."""
        self.client.force_authenticate(user=self.admin_user)
        data = {'nombre': 'Suite Presidencial'} # Ya existe
        response = self.client.post(self.list_create_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['nombre'][0], 'Ya existe un tipo de habitación con ese nombre.')


class HabitacionAPITests(APITestCase):
    def setUp(self):
        self.admin_user = Usuario.objects.create_user(username='admin', password='password123', rol=Usuario.Rol.ADMINISTRADOR)
        self.employee_user = Usuario.objects.create_user(username='employee', password='password123', rol=Usuario.Rol.EMPLEADO)
        self.tipo_activo = TipoHabitacion.objects.create(nombre="Sencilla", activo=True)
        self.tipo_inactivo = TipoHabitacion.objects.create(nombre="Doble", activo=False)
        self.habitacion1 = Habitacion.objects.create(numero=101, tipo=self.tipo_activo)
        self.habitacion2 = Habitacion.objects.create(numero=102, tipo=self.tipo_activo, activa=False)

        self.list_create_url = reverse('habitaciones_list')

    def test_empleado_puede_listar_habitaciones(self):
        """Prueba que un empleado puede listar todas las habitaciones."""
        self.client.force_authenticate(user=self.employee_user)
        response = self.client.get(self.list_create_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get('results', response.data)
        self.assertEqual(len(results), 2) # Should return both active and inactive

    def test_filtrar_habitaciones_activas(self):
        """Prueba que se puede filtrar por habitaciones activas."""
        self.client.force_authenticate(user=self.employee_user)
        response = self.client.get(self.list_create_url, {'activa': 'true'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get('results', response.data)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['numero'], 101)

    def test_admin_puede_crear_habitacion(self):
        """Prueba que un admin puede crear una habitación."""
        self.client.force_authenticate(user=self.admin_user)
        data = {'numero': 103, 'tipo': self.tipo_activo.pk}
        response = self.client.post(self.list_create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Habitacion.objects.count(), 3)

    def test_crear_habitacion_duplicada_falla_api(self):
        """Prueba que la API no permite crear habitaciones con el mismo número."""
        self.client.force_authenticate(user=self.admin_user)
        data = {'numero': 101, 'tipo': self.tipo_activo.pk} # El número 101 ya existe
        response = self.client.post(self.list_create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['numero'][0], 'Ya existe una habitación con ese número.')

    def test_crear_habitacion_con_tipo_inactivo_falla_api(self):
        """Prueba que la API no permite crear una habitación con un tipo inactivo."""
        self.client.force_authenticate(user=self.admin_user)
        data = {'numero': 201, 'tipo': self.tipo_inactivo.pk}
        response = self.client.post(self.list_create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['tipo'][0], 'No se puede asignar una habitación a un tipo inactivo.')
