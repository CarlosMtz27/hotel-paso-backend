from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from decimal import Decimal
from django.core.exceptions import ValidationError

from apps.users.models import Usuario
from apps.turnos.models import Turno
from apps.productos.models import Producto
from .models import MovimientoCaja


class CajaAPITests(APITestCase):
    def setUp(self):
        # --- Users ---
        self.admin_user = Usuario.objects.create_user(username='admin', password='password123', rol=Usuario.Rol.ADMINISTRADOR)
        self.employee_user = Usuario.objects.create_user(username='employee', password='password123', rol=Usuario.Rol.EMPLEADO)

        # --- Datos ---
        self.turno_activo = Turno.objects.create(usuario=self.employee_user, tipo_turno="DIA", activo=True)
        self.producto_activo = Producto.objects.create(nombre="Refresco", precio="50.00", activo=True)
        self.producto_inactivo = Producto.objects.create(nombre="Snack", precio="30.00", activo=False)

        # --- URLs ---
        self.movimientos_url = reverse('movimientos-list-create')

    def test_admin_puede_listar_movimientos(self):
        """Un admin puede listar los movimientos de caja."""
        MovimientoCaja.objects.create(turno=self.turno_activo, tipo="PRODUCTO", monto=50, metodo_pago="EFECTIVO", producto=self.producto_activo)
        
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.movimientos_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['results'] if 'results' in response.data else response.data
        self.assertEqual(len(results), 1)

    def test_empleado_no_puede_listar_movimientos(self):
        """Un empleado no puede listar los movimientos de caja."""
        self.client.force_authenticate(user=self.employee_user)
        response = self.client.get(self.movimientos_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_crear_movimiento_venta_producto(self):
        """Un empleado puede registrar la venta de un producto y recibe el objeto completo."""
        self.client.force_authenticate(user=self.employee_user)
        data = {"producto_id": self.producto_activo.id, "cantidad": 3, "metodo_pago": "EFECTIVO"}
        response = self.client.post(self.movimientos_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(MovimientoCaja.objects.count(), 1)
        movimiento = MovimientoCaja.objects.first()
        self.assertEqual(movimiento.monto, Decimal("150.00"))
        self.assertEqual(response.data['monto'], "150.00")
        self.assertEqual(response.data['producto'], str(self.producto_activo))

    def test_crear_movimiento_falla_sin_turno_activo(self):
        """La venta de un producto falla si no hay turno activo."""
        self.turno_activo.activo = False
        self.turno_activo.save()
        
        self.client.force_authenticate(user=self.employee_user)
        data = {"producto_id": self.producto_activo.id, "cantidad": 1, "metodo_pago": "EFECTIVO"}
        response = self.client.post(self.movimientos_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("No hay un turno activo", str(response.data))

    def test_modelo_movimiento_requiere_estancia(self):
        """El modelo MovimientoCaja valida que los tipos ESTANCIA/EXTRA requieren una estancia."""
        with self.assertRaisesMessage(ValidationError, "Este movimiento requiere una estancia"):
            MovimientoCaja.objects.create(
                turno=self.turno_activo, tipo="ESTANCIA", monto=100, metodo_pago="EFECTIVO"
            )
