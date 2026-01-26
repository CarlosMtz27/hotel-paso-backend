from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.utils import timezone
from dateutil.parser import parse
from datetime import timedelta

from apps.users.models import Usuario
from apps.turnos.models import Turno
from apps.habitaciones.models import TipoHabitacion, Habitacion
from apps.tarifas.models import Tarifa
from apps.caja.models import MovimientoCaja
from .models import Estancia


class EstanciaAPITests(APITestCase):
    def setUp(self):
        # --- Users and Permissions ---
        self.admin_user = Usuario.objects.create_user(username='admin', password='password123', rol=Usuario.Rol.ADMINISTRADOR)
        self.employee_user = Usuario.objects.create_user(username='employee', password='password123', rol=Usuario.Rol.EMPLEADO)

        # --- Base Data ---
        self.tipo_sencilla = TipoHabitacion.objects.create(nombre="Sencilla")
        self.habitacion_101 = Habitacion.objects.create(numero="101", tipo=self.tipo_sencilla, activa=True)
        self.habitacion_inactiva = Habitacion.objects.create(numero="102", tipo=self.tipo_sencilla, activa=False)

        self.tarifa_3h = Tarifa.objects.create(nombre="3 Horas", horas=3, precio=500, tipo_habitacion=self.tipo_sencilla, activa=True)
        self.tarifa_inactiva = Tarifa.objects.create(nombre="Tarifa Inactiva", horas=1, precio=100, tipo_habitacion=self.tipo_sencilla, activa=False)

        # --- Active Shift ---
        self.turno_activo = Turno.objects.create(usuario=self.employee_user, tipo_turno="DIA", caja_inicial=1000, activo=True)

        # --- URLs ---
        self.abrir_url = reverse('abrir-estancia')
        self.cerrar_url = reverse('cerrar-estancia')
        self.agregar_horas_url = reverse('agregar-horas-extra')

    def test_abrir_estancia_exitoso(self):
        """Reglas 1, 2, 3, 4: Abrir una estancia correctamente, calculando salida y creando movimiento."""
        self.client.force_authenticate(user=self.employee_user)
        data = {
            "habitacion_id": self.habitacion_101.id,
            "tarifa_id": self.tarifa_3h.id,
            "metodo_pago": "EFECTIVO"
        }
        response = self.client.post(self.abrir_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Verificar que la respuesta devuelve el objeto completo
        self.assertEqual(response.data['habitacion'], str(self.habitacion_101))
        self.assertTrue(response.data['activa'])

        # Verificar estado de la DB
        self.assertTrue(Estancia.objects.filter(habitacion=self.habitacion_101, activa=True).exists())
        estancia = Estancia.objects.get(habitacion=self.habitacion_101, activa=True)

        # Regla 1: Se asocia al turno activo y se marca como activa
        self.assertEqual(estancia.turno_inicio, self.turno_activo)
        self.assertTrue(estancia.activa)

        # Regla 2: La hora de salida se calcula automáticamente
        salida_esperada = estancia.hora_entrada + timedelta(hours=self.tarifa_3h.horas)
        self.assertAlmostEqual(estancia.hora_salida_programada, salida_esperada, delta=timedelta(seconds=1))

        # Reglas 3 y 4: Se crea un movimiento de caja con el precio completo
        self.assertTrue(MovimientoCaja.objects.filter(estancia=estancia, tipo="ESTANCIA").exists())
        movimiento = MovimientoCaja.objects.get(estancia=estancia, tipo="ESTANCIA")
        self.assertEqual(movimiento.monto, self.tarifa_3h.precio)
        self.assertEqual(movimiento.metodo_pago, "EFECTIVO")
        self.assertEqual(movimiento.turno, self.turno_activo)

    def test_abrir_estancia_falla_sin_turno_activo(self):
        """Regla 1: No se puede abrir si no hay turno activo."""
        self.turno_activo.activo = False
        self.turno_activo.save()

        self.client.force_authenticate(user=self.employee_user)
        data = {"habitacion_id": self.habitacion_101.id, "tarifa_id": self.tarifa_3h.id, "metodo_pago": "EFECTIVO"}
        response = self.client.post(self.abrir_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("No hay un turno activo", str(response.data))

    def test_abrir_estancia_falla_habitacion_ocupada(self):
        """Regla 1: No se puede abrir si la habitación ya está ocupada."""
        Estancia.objects.create(
            habitacion=self.habitacion_101, tarifa=self.tarifa_3h, turno_inicio=self.turno_activo,
            hora_salida_programada=timezone.now() + timedelta(hours=3)
        )
        self.client.force_authenticate(user=self.employee_user)
        data = {"habitacion_id": self.habitacion_101.id, "tarifa_id": self.tarifa_3h.id, "metodo_pago": "EFECTIVO"}
        response = self.client.post(self.abrir_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("La habitación ya está ocupada", str(response.data))

    def test_abrir_estancia_falla_habitacion_inactiva(self):
        """Regla 1: No se puede abrir con habitación inactiva."""
        self.client.force_authenticate(user=self.employee_user)
        data = {"habitacion_id": self.habitacion_inactiva.id, "tarifa_id": self.tarifa_3h.id, "metodo_pago": "EFECTIVO"}
        response = self.client.post(self.abrir_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("La habitación no está activa", str(response.data))

    def test_agregar_horas_extra_exitoso(self):
        """Regla 5: Agregar horas extra extiende la salida y crea movimiento."""
        estancia = Estancia.objects.create(
            habitacion=self.habitacion_101, tarifa=self.tarifa_3h, turno_inicio=self.turno_activo,
            hora_salida_programada=timezone.now() + timedelta(hours=3)
        )
        salida_original = estancia.hora_salida_programada

        self.client.force_authenticate(user=self.employee_user)
        data = {
            "estancia_id": estancia.id, "cantidad_horas": 2, "precio_hora": "150.00", "metodo_pago": "TRANSFERENCIA"
        }
        response = self.client.post(self.agregar_horas_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verificar que la respuesta devuelve el objeto actualizado
        self.assertEqual(response.data['id'], estancia.id)
        # Parse datetime from response to compare timezone-aware objects
        response_dt = parse(response.data['hora_salida_programada'])
        self.assertEqual(response_dt, salida_original + timedelta(hours=2))

        estancia.refresh_from_db()
        self.assertEqual(estancia.hora_salida_programada, salida_original + timedelta(hours=2))
        movimiento = MovimientoCaja.objects.get(estancia=estancia, tipo="EXTRA")
        self.assertEqual(movimiento.monto, 300.00)
        self.assertEqual(movimiento.metodo_pago, "TRANSFERENCIA")

    def test_cerrar_estancia_exitoso(self):
        """Regla 7: Cerrar una estancia correctamente."""
        estancia = Estancia.objects.create(
            habitacion=self.habitacion_101, tarifa=self.tarifa_3h, turno_inicio=self.turno_activo,
            hora_salida_programada=timezone.now() + timedelta(hours=3)
        )
        self.client.force_authenticate(user=self.employee_user)
        data = {"estancia_id": estancia.id}
        response = self.client.post(self.cerrar_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verificar que la respuesta devuelve el objeto actualizado
        self.assertFalse(response.data['activa'])
        self.assertIsNotNone(response.data['hora_salida_real'])

        estancia.refresh_from_db()
        self.assertFalse(estancia.activa)
        self.assertEqual(estancia.turno_cierre, self.turno_activo)
        self.assertIsNotNone(estancia.hora_salida_real)

    def test_cerrar_estancia_en_turno_posterior(self):
        """Regla 8: Una estancia puede cerrarse en un turno distinto al que se abrió."""
        estancia = Estancia.objects.create(
            habitacion=self.habitacion_101, tarifa=self.tarifa_3h, turno_inicio=self.turno_activo,
            hora_salida_programada=timezone.now() + timedelta(hours=3)
        )
        self.turno_activo.activo = False
        self.turno_activo.save()
        turno_posterior = Turno.objects.create(usuario=self.admin_user, tipo_turno="NOCHE", activo=True)

        self.client.force_authenticate(user=self.admin_user)
        data = {"estancia_id": estancia.id}
        response = self.client.post(self.cerrar_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verificar que la respuesta devuelve el objeto actualizado
        self.assertFalse(response.data['activa'])
        self.assertEqual(response.data['turno_cierre'], str(turno_posterior))

        estancia.refresh_from_db()
        self.assertFalse(estancia.activa)
        self.assertEqual(estancia.turno_inicio, self.turno_activo)
        self.assertEqual(estancia.turno_cierre, turno_posterior)
