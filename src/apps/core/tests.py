from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from decimal import Decimal
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

from apps.users.models import Usuario
from apps.habitaciones.models import TipoHabitacion, Habitacion
from apps.tarifas.models import Tarifa
from apps.productos.models import Producto
from apps.turnos.models import Turno
from apps.estancias.models import Estancia
from apps.caja.models import MovimientoCaja


class EndToEndWorkflowTest(APITestCase):
    """
    Prueba de integración de extremo a extremo que simula un flujo de negocio completo.
    1. Admin configura el hotel (habitaciones, tarifas, productos).
    2. Empleado inicia un turno.
    3. Empleado abre una estancia.
    4. Empleado vende un producto a esa estancia.
    5. Empleado agrega horas extra.
    6. Empleado cierra el turno y se verifican los cálculos finales.
    """

    def setUp(self):
        # --- 1. Admin configura el hotel ---
        self.admin_user = Usuario.objects.create_user(username='admin', password='password123', rol=Usuario.Rol.ADMINISTRADOR)
        self.employee_user = Usuario.objects.create_user(username='employee', password='password123', rol=Usuario.Rol.EMPLEADO)

        # Asignar permisos necesarios al empleado
        turno_content_type = ContentType.objects.get_for_model(Turno)
        perm_abrir = Permission.objects.get(content_type=turno_content_type, codename='abrir_turno')
        perm_cerrar = Permission.objects.get(content_type=turno_content_type, codename='cerrar_turno')
        self.employee_user.user_permissions.add(perm_abrir, perm_cerrar)

        self.tipo_sencilla = TipoHabitacion.objects.create(nombre="Sencilla")
        self.habitacion_101 = Habitacion.objects.create(numero=101, tipo=self.tipo_sencilla)
        self.tarifa_3h = Tarifa.objects.create(nombre="3 Horas", horas=3, precio=500, tipo_habitacion=self.tipo_sencilla)
        self.producto_refresco = Producto.objects.create(nombre="Refresco", precio=50)

    def test_full_business_cycle(self):
        # --- 2. Empleado inicia un turno ---
        self.client.force_authenticate(user=self.employee_user)
        iniciar_turno_url = reverse('iniciar-turno')
        iniciar_turno_data = {"tipo_turno": "DIA", "caja_inicial": "1000.00"}
        response = self.client.post(iniciar_turno_url, iniciar_turno_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        turno_id = response.data['id']

        # --- 3. Empleado abre una estancia ---
        abrir_estancia_url = reverse('abrir-estancia')
        abrir_estancia_data = {
            "habitacion_id": self.habitacion_101.id,
            "tarifa_id": self.tarifa_3h.id,
            "metodo_pago": "EFECTIVO"
        }
        response = self.client.post(abrir_estancia_url, abrir_estancia_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        estancia_id = response.data['id']

        # --- 4. Empleado vende un producto a esa estancia ---
        vender_producto_url = reverse('movimientos-list-create')
        venta_data = {
            "producto_id": self.producto_refresco.id,
            "cantidad": 2,
            "metodo_pago": "EFECTIVO",
            "estancia_id": estancia_id
        }
        response = self.client.post(vender_producto_url, venta_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # --- 5. Empleado agrega horas extra ---
        agregar_horas_url = reverse('agregar-horas-extra')
        horas_extra_data = {
            "estancia_id": estancia_id,
            "cantidad_horas": 1,
            "precio_hora": "150.00",
            "metodo_pago": "TRANSFERENCIA"
        }
        response = self.client.post(agregar_horas_url, horas_extra_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # --- 6. Empleado cierra el turno y se verifican los cálculos ---
        cerrar_turno_url = reverse('cerrar-turno')
        # Caja inicial: 1000, Estancia: 500 (efectivo), Productos: 100 (efectivo) -> Total Efectivo: 600
        # Horas Extra: 150 (transferencia)
        # Sueldo: 200
        # Efectivo esperado = 1000 + 600 - 200 = 1400
        # El empleado cuenta 1405 (5 de propina)
        cerrar_turno_data = {"efectivo_reportado": "1405.00", "sueldo": "200.00"}
        response = self.client.post(cerrar_turno_url, cerrar_turno_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        resumen = response.data['resumen']
        self.assertEqual(Decimal(resumen['total_ingresos']), Decimal('750.00')) # 500 + 100 + 150
        self.assertEqual(Decimal(resumen['efectivo_esperado']), Decimal('1400.00'))
        self.assertEqual(Decimal(resumen['diferencia']), Decimal('5.00'))