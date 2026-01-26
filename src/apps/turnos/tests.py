from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from decimal import Decimal
from django.utils import timezone

from apps.users.models import Usuario
from .models import Turno
from apps.caja.models import MovimientoCaja
from apps.habitaciones.models import TipoHabitacion, Habitacion
from apps.tarifas.models import Tarifa
from apps.estancias.models import Estancia
from django.core.exceptions import ValidationError
from apps.productos.models import Producto


class TurnoAPITests(APITestCase):
    def setUp(self):
        # Crear usuarios
        self.admin_user = Usuario.objects.create_user(username='admin', password='password123', rol=Usuario.Rol.ADMINISTRADOR)
        self.employee_auth = Usuario.objects.create_user(username='emp_auth', password='password123', rol=Usuario.Rol.EMPLEADO)
        self.employee_other = Usuario.objects.create_user(username='other_emp', password='password123', rol=Usuario.Rol.EMPLEADO)
        self.employee_no_perms = Usuario.objects.create_user(username='emp_unauth', password='password123', rol=Usuario.Rol.EMPLEADO)

        # Asignar permisos de Django
        content_type = ContentType.objects.get_for_model(Turno)
        perm_abrir = Permission.objects.get(content_type=content_type, codename='abrir_turno')
        perm_cerrar = Permission.objects.get(content_type=content_type, codename='cerrar_turno')
        self.employee_auth.user_permissions.add(perm_abrir, perm_cerrar)
        self.employee_other.user_permissions.add(perm_abrir, perm_cerrar)
        self.admin_user.user_permissions.add(perm_abrir, perm_cerrar)

        # Crear objetos necesarios para estancias
        self.tipo_sencilla = TipoHabitacion.objects.create(nombre="Sencilla")
        self.habitacion_101 = Habitacion.objects.create(numero="101", tipo=self.tipo_sencilla)
        self.habitacion_102 = Habitacion.objects.create(numero="102", tipo=self.tipo_sencilla)
        self.tarifa_3h = Tarifa.objects.create(
            nombre="3 Horas",
            horas=3,
            precio=500,
            tipo_habitacion=self.tipo_sencilla
        )
        self.tarifa_6h = Tarifa.objects.create(
            nombre="6 Horas",
            horas=6,
            precio=300,
            tipo_habitacion=self.tipo_sencilla
        )
        self.producto_test = Producto.objects.create(nombre="Refresco", precio=50)

        # URLs
        self.iniciar_url = reverse('iniciar-turno')
        self.cerrar_url = reverse('cerrar-turno')
        self.list_url = reverse('turnos-list')

    def test_abrir_turno_exitoso(self):
        """Regla 1: Un empleado autorizado puede abrir un turno."""
        self.client.force_authenticate(user=self.employee_auth)
        data = {"tipo_turno": "DIA", "caja_inicial": "1000.00"}
        response = self.client.post(self.iniciar_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Turno.objects.filter(usuario=self.employee_auth, activo=True).exists())
        self.assertEqual(response.data['usuario'], str(self.employee_auth))
        self.assertEqual(response.data['tipo_turno'], 'DIA')
        self.assertEqual(Decimal(response.data['caja_inicial']), Decimal('1000.00'))
        self.assertTrue(response.data['activo'])

    def test_abrir_turno_falla_si_ya_hay_uno_activo(self):
        """Regla 1: Solo puede existir un turno activo a la vez."""
        # Abrimos un primer turno
        Turno.objects.create(usuario=self.employee_other, tipo_turno="DIA", activo=True)
        
        self.client.force_authenticate(user=self.employee_auth)
        data = {"tipo_turno": "DIA", "caja_inicial": "1000.00"}
        response = self.client.post(self.iniciar_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Ya existe un turno activo", str(response.data))

    def test_abrir_turno_falla_sin_permiso(self):
        """Regla 1: El turno lo abre un empleado autorizado."""
        self.client.force_authenticate(user=self.employee_no_perms)
        data = {"tipo_turno": "DIA", "caja_inicial": "1000.00"}
        response = self.client.post(self.iniciar_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("No tienes permiso para abrir turno", str(response.data))

    def test_cerrar_turno_falla_por_otro_empleado(self):
        """Regla 2: Un empleado solo puede cerrar su propio turno."""
        Turno.objects.create(usuario=self.employee_auth, tipo_turno="DIA", activo=True)
        
        # Intentamos cerrar con otro usuario
        self.client.force_authenticate(user=self.employee_other)
        data = {"efectivo_reportado": "1000.00", "sueldo": "0"}
        response = self.client.post(self.cerrar_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Solo puedes cerrar tu propio turno", str(response.data))

    def test_cierre_de_turno_calculos_correctos(self):
        """Regla 7: Verifica los cálculos al cerrar el turno."""
        turno = Turno.objects.create(usuario=self.employee_auth, tipo_turno="DIA", caja_inicial=1000, activo=True)

        hora_actual = timezone.now()

        # Crear estancias para poder crear movimientos de caja de tipo ESTANCIA
        estancia1 = Estancia.objects.create(
            habitacion=self.habitacion_101,
            tarifa=self.tarifa_3h,
            turno_inicio=turno,
            activa=True,
            hora_salida_programada=hora_actual + timezone.timedelta(hours=self.tarifa_3h.horas)
        )
        estancia2 = Estancia.objects.create(
            habitacion=self.habitacion_102,
            tarifa=self.tarifa_6h,
            turno_inicio=turno,
            activa=True,
            hora_salida_programada=hora_actual + timezone.timedelta(hours=self.tarifa_6h.horas)
        )

        # Simulamos ingresos en efectivo
        MovimientoCaja.objects.create(turno=turno, monto=500, metodo_pago="EFECTIVO", tipo="ESTANCIA", estancia=estancia1)
        MovimientoCaja.objects.create(turno=turno, monto=200, metodo_pago="EFECTIVO", tipo="PRODUCTO", producto=self.producto_test)
        # Simulamos ingresos por transferencia (no deben afectar el efectivo)
        MovimientoCaja.objects.create(turno=turno, monto=300, metodo_pago="TRANSFERENCIA", tipo="ESTANCIA", estancia=estancia2)

        self.client.force_authenticate(user=self.employee_auth)
        # El empleado se lleva 150 de sueldo y cuenta 1560 en caja
        data = {"efectivo_reportado": "1560.00", "sueldo": "150.00"}
        response = self.client.post(self.cerrar_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificamos los cálculos
        # Esperado = 1000 (inicial) + 700 (efectivo) - 150 (sueldo) = 1550
        # Reportado = 1560
        # Diferencia = 1560 - 1550 = 10
        resumen = response.data['resumen']
        self.assertEqual(Decimal(resumen['efectivo_esperado']), Decimal("1550.00"))
        self.assertEqual(Decimal(resumen['diferencia']), Decimal("10.00"))

    def test_cierre_de_turno_sin_ingresos(self):
        """Regla 8: Verifica la bandera sin_ingresos."""
        Turno.objects.create(usuario=self.employee_auth, tipo_turno="DIA", caja_inicial=1000, activo=True)
        
        self.client.force_authenticate(user=self.employee_auth)
        data = {"efectivo_reportado": "1000.00", "sueldo": "0"}
        response = self.client.post(self.cerrar_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['sin_ingresos'])

    def test_admin_puede_listar_turnos(self):
        """Prueba que un admin puede listar todos los turnos."""
        Turno.objects.create(usuario=self.employee_auth, tipo_turno="DIA", activo=False)
        Turno.objects.create(usuario=self.employee_other, tipo_turno="NOCHE", activo=True)

        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Handle both paginated and non-paginated responses
        if 'results' in response.data:
            self.assertEqual(response.data['count'], 2)
            self.assertEqual(len(response.data['results']), 2)
        else:
            self.assertEqual(len(response.data), 2)

    def test_empleado_no_puede_listar_turnos(self):
        """Prueba que un empleado sin rol de admin no puede listar turnos."""
        self.client.force_authenticate(user=self.employee_auth)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_filtrar_turnos_por_usuario(self):
        """Prueba el filtrado de turnos por usuario."""
        Turno.objects.create(usuario=self.employee_auth, tipo_turno="DIA", activo=False)
        Turno.objects.create(usuario=self.employee_other, tipo_turno="NOCHE", activo=True)

        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.list_url, {'usuario': self.employee_other.pk})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Handle both paginated and non-paginated responses
        if 'results' in response.data:
            results = response.data['results']
            self.assertEqual(response.data['count'], 1)
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0]['usuario'], str(self.employee_other))
        else:
            results = response.data
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0]['usuario'], str(self.employee_other))

    def test_modelo_caja_inicial_negativa_falla(self):
        """Prueba que el modelo no permite una caja inicial negativa."""
        with self.assertRaises(ValidationError):
            Turno.objects.create(
                usuario=self.employee_auth,
                tipo_turno="DIA",
                caja_inicial=-100,
                activo=True
            )
