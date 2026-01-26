from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from decimal import Decimal

from apps.users.models import Usuario
from apps.turnos.models import Turno
from apps.caja.models import MovimientoCaja
from apps.habitaciones.models import TipoHabitacion, Habitacion
from apps.tarifas.models import Tarifa
from apps.estancias.models import Estancia
from apps.productos.models import Producto


class ReportesAPITests(APITestCase):
    def setUp(self):
        # --- Users ---
        self.admin_user = Usuario.objects.create_user(username='admin', password='password123', rol=Usuario.Rol.ADMINISTRADOR)
        self.employee1 = Usuario.objects.create_user(username='empleado1', password='password123', rol=Usuario.Rol.EMPLEADO)
        self.employee2 = Usuario.objects.create_user(username='empleado2', password='password123', rol=Usuario.Rol.EMPLEADO)

        # --- Base Data ---
        self.tipo_sencilla = TipoHabitacion.objects.create(nombre="Sencilla")
        self.habitacion_101 = Habitacion.objects.create(numero=101, tipo=self.tipo_sencilla)
        self.habitacion_102 = Habitacion.objects.create(numero=102, tipo=self.tipo_sencilla)
        self.tarifa_base = Tarifa.objects.create(nombre="Tarifa Base", horas=3, precio=1000, tipo_habitacion=self.tipo_sencilla)
        self.producto_base = Producto.objects.create(nombre="Refresco", precio=150)

        # --- Turnos y Movimientos ---
        # Turno 1 para empleado 1 con movimientos
        # Se crea el turno como ACTIVO
        turno1_emp1 = Turno.objects.create(usuario=self.employee1, tipo_turno="DIA", activo=True, caja_inicial=1000)
        estancia1 = Estancia.objects.create(habitacion=self.habitacion_101, tarifa=self.tarifa_base, turno_inicio=turno1_emp1, hora_salida_programada=turno1_emp1.fecha_inicio)
        # Se crean los movimientos MIENTRAS el turno está activo
        MovimientoCaja.objects.create(turno=turno1_emp1, tipo="ESTANCIA", monto=1000, metodo_pago="EFECTIVO", estancia=estancia1)
        MovimientoCaja.objects.create(turno=turno1_emp1, tipo="PRODUCTO", monto=150, metodo_pago="TRANSFERENCIA", producto=self.producto_base)
        # Se cierra el turno DESPUÉS de crear los movimientos
        turno1_emp1.activo = False
        turno1_emp1.save()
        self.turno1_emp1 = turno1_emp1

        # Turno 2 para empleado 1 sin movimientos
        self.turno2_emp1 = Turno.objects.create(usuario=self.employee1, tipo_turno="NOCHE", activo=False)

        # Turno 1 para empleado 2 con movimientos
        self.turno1_emp2 = Turno.objects.create(usuario=self.employee2, tipo_turno="DIA", activo=True)
        estancia2 = Estancia.objects.create(habitacion=self.habitacion_102, tarifa=self.tarifa_base, turno_inicio=self.turno1_emp2, hora_salida_programada=self.turno1_emp2.fecha_inicio)
        MovimientoCaja.objects.create(turno=self.turno1_emp2, tipo="ESTANCIA", monto=2000, metodo_pago="EFECTIVO", estancia=estancia2)

        # --- URLs ---
        self.reporte_turnos_url = reverse('reporte-turnos')
        self.reporte_empleados_url = reverse('reporte-empleados')

    def test_admin_puede_ver_reporte_turnos(self):
        """Prueba que un admin puede ver el reporte de todos los turnos."""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.reporte_turnos_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        results = response.data['results'] if 'results' in response.data else response.data
        self.assertEqual(len(results), 3) # Debe ver los 3 turnos
        
        # Verificar que los totales son correctos para el primer turno
        turno1_data = next(t for t in results if t['turno_id'] == self.turno1_emp1.id)
        self.assertEqual(Decimal(turno1_data['total_ingresos']), Decimal('1150.00'))
        self.assertEqual(Decimal(turno1_data['total_efectivo']), Decimal('1000.00'))

    def test_empleado_no_puede_ver_reporte_turnos(self):
        """Prueba que un empleado no puede acceder a reportes generales."""
        self.client.force_authenticate(user=self.employee1)
        response = self.client.get(self.reporte_turnos_url)
        # La vista ahora requiere permisos de admin
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_puede_ver_reporte_empleados(self):
        """Prueba que un admin puede ver el reporte agregado por empleado."""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.reporte_empleados_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = response.data['results'] if 'results' in response.data else response.data
        self.assertEqual(len(results), 2) # Debe haber 2 empleados en el reporte

        # Verificar datos del empleado 1
        emp1_data = next(e for e in results if e['empleado_id'] == self.employee1.id)
        self.assertEqual(emp1_data['turnos'], 2)
        self.assertEqual(emp1_data['turnos_sin_ingresos'], 1)
        self.assertEqual(Decimal(emp1_data['total_ingresos']), Decimal('1150.00'))