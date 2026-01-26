from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.users.models import Usuario
from apps.habitaciones.models import TipoHabitacion
from .models import Tarifa


class TarifaAPITests(APITestCase):
    def setUp(self):
        # Crear usuarios con diferentes roles
        self.admin_user = Usuario.objects.create_user(username='admin', password='password123', rol=Usuario.Rol.ADMINISTRADOR)
        self.employee_user = Usuario.objects.create_user(username='employee', password='password123', rol=Usuario.Rol.EMPLEADO)

        # Crear un tipo de habitación para asociar a las tarifas
        self.tipo_sencilla = TipoHabitacion.objects.create(nombre="Sencilla")

        # Crear una tarifa de prueba
        self.tarifa = Tarifa.objects.create(
            nombre="3 Horas",
            horas=3,
            precio=300.00,
            tipo_habitacion=self.tipo_sencilla
        )

        # URLs
        self.list_create_url = reverse('tarifas_list_create')
        self.detail_url = reverse('tarifas_detail', kwargs={'pk': self.tarifa.pk})

    def test_empleado_puede_listar_tarifas(self):
        """Prueba que un empleado puede listar las tarifas existentes."""
        self.client.force_authenticate(user=self.employee_user)
        response = self.client.get(self.list_create_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Maneja respuestas paginadas y no paginadas para mayor robustez.
        results = response.data.get('results', response.data)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['nombre'], '3 Horas')

    def test_admin_puede_crear_tarifa(self):
        """Prueba que un administrador puede crear una tarifa."""
        self.client.force_authenticate(user=self.admin_user)
        data = {
            "nombre": "6 Horas",
            "horas": 6,
            "precio": "500.00",
            "tipo_habitacion": self.tipo_sencilla.pk
        }
        response = self.client.post(self.list_create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Tarifa.objects.count(), 2)

    def test_empleado_no_puede_crear_tarifa(self):
        """Prueba que un empleado no puede crear una tarifa."""
        self.client.force_authenticate(user=self.employee_user)
        data = {"nombre": "Tarifa Empleado", "horas": 1, "precio": "100.00", "tipo_habitacion": self.tipo_sencilla.pk}
        response = self.client.post(self.list_create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_puede_actualizar_tarifa(self):
        """Prueba que un administrador puede actualizar una tarifa."""
        self.client.force_authenticate(user=self.admin_user)
        data = {"precio": "350.00", "activa": False}
        response = self.client.patch(self.detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.tarifa.refresh_from_db()
        self.assertEqual(self.tarifa.precio, 350.00)
        self.assertFalse(self.tarifa.activa)

    def test_empleado_no_puede_actualizar_tarifa(self):
        """Prueba que un empleado no puede actualizar una tarifa."""
        self.client.force_authenticate(user=self.employee_user)
        data = {"precio": "350.00"}
        response = self.client.patch(self.detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_puede_eliminar_tarifa(self):
        """Prueba que un administrador puede eliminar una tarifa."""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Tarifa.objects.count(), 0)

    # --- Pruebas de Lógica de Negocio ---

    def test_crear_tarifa_nocturna_sin_horario_falla(self):
        """Prueba que la API no permite crear una tarifa nocturna sin su horario."""
        self.client.force_authenticate(user=self.admin_user)
        data = {
            "nombre": "Noche Incompleta",
            "horas": 12,
            "precio": "800.00",
            "tipo_habitacion": self.tipo_sencilla.pk,
            "es_nocturna": True
            # Falta hora_inicio_nocturna y hora_fin_nocturna
        }
        response = self.client.post(self.list_create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Las tarifas nocturnas deben tener una hora de inicio y fin.", str(response.data))

    def test_crear_tarifa_duplicada_falla(self):
        """Prueba que no se puede crear una tarifa con el mismo nombre y tipo de habitación."""
        self.client.force_authenticate(user=self.admin_user)
        data = {
            "nombre": "3 Horas",  # Nombre y tipo ya existen
            "horas": 4,
            "precio": "400.00",
            "tipo_habitacion": self.tipo_sencilla.pk
        }
        response = self.client.post(self.list_create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Ya existe una tarifa con este nombre para el tipo de habitación seleccionado.", str(response.data))
