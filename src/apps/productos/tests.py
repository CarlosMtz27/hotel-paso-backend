from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.core.exceptions import ValidationError

from apps.users.models import Usuario
from apps.caja.services import vender_producto
from apps.turnos.models import Turno
from .models import Producto


class ProductoAPITests(APITestCase):
    def setUp(self):
        # Crear usuarios con diferentes roles
        self.admin_user = Usuario.objects.create_user(username='admin', password='password123', rol=Usuario.Rol.ADMINISTRADOR)
        self.employee_user = Usuario.objects.create_user(username='employee', password='password123', rol=Usuario.Rol.EMPLEADO)

        # Crear un producto de prueba
        self.producto = Producto.objects.create(nombre="Agua Mineral", precio=100.00, stock=20)

        # URLs
        self.list_create_url = reverse('productos_list')
        self.detail_url = reverse('productos_detail', kwargs={'pk': self.producto.pk})

    def test_admin_puede_crear_producto(self):
        """Prueba que un administrador puede crear un producto."""
        self.client.force_authenticate(user=self.admin_user)
        data = {'nombre': 'Jugo de Naranja', 'precio': '120.50', 'stock': 15}
        response = self.client.post(self.list_create_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Producto.objects.count(), 2)
        nuevo_producto = Producto.objects.get(nombre='Jugo de Naranja')
        self.assertEqual(nuevo_producto.stock, 15)

    def test_empleado_no_puede_crear_producto(self):
        """Prueba que un empleado no puede crear un producto."""
        self.client.force_authenticate(user=self.employee_user)
        data = {'nombre': 'Jugo de Naranja', 'precio': '120.50', 'stock': 10}
        response = self.client.post(self.list_create_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_puede_actualizar_producto(self):
        """Prueba que un administrador puede actualizar un producto."""
        self.client.force_authenticate(user=self.admin_user)
        data = {'nombre': 'Agua con Gas', 'precio': '110.00', 'stock': 25, 'activo': False}
        response = self.client.put(self.detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.nombre, 'Agua con Gas')
        self.assertEqual(self.producto.stock, 25)
        self.assertFalse(self.producto.activo)

    def test_empleado_no_puede_actualizar_producto(self):
        """Prueba que un empleado no puede actualizar un producto."""
        self.client.force_authenticate(user=self.employee_user)
        data = {'nombre': 'Agua con Gas', 'precio': '110.00', 'stock': 5}
        response = self.client.put(self.detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_crear_producto_duplicado_falla_api(self):
        """Prueba que la API no permite crear productos con el mismo nombre."""
        self.client.force_authenticate(user=self.admin_user)
        data = {'nombre': 'Agua Mineral', 'precio': '150.00', 'stock': 10}  # 'Agua Mineral' ya existe
        response = self.client.post(self.list_create_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['nombre'][0], 'Ya existe un producto con ese nombre.')

    def test_crear_producto_precio_invalido_falla_api(self):
        """Prueba que la API no permite crear productos con precio cero o negativo."""
        self.client.force_authenticate(user=self.admin_user)
        data = {'nombre': 'Nuevo Producto', 'precio': '0.00', 'stock': 10}
        response = self.client.post(self.list_create_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['precio'][0], 'El precio debe ser mayor a cero.')

    def test_filtrar_productos_activos(self):
        """Prueba que se puede filtrar por productos activos."""
        Producto.objects.create(nombre="Papas Fritas", precio=150, stock=10, activo=False)
        self.client.force_authenticate(user=self.employee_user)
        response = self.client.get(self.list_create_url, {'activo': 'true'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get('results', response.data)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['nombre'], 'Agua Mineral')

    def test_vender_producto_reduce_stock(self):
        """Prueba que el servicio vender_producto reduce el stock correctamente."""
        turno = Turno.objects.create(usuario=self.employee_user, tipo_turno=Turno.TipoTurno.DIA)
        producto_a_vender = self.producto
        stock_inicial = producto_a_vender.stock
        cantidad_vendida = 2

        vender_producto(
            producto=producto_a_vender,
            cantidad=cantidad_vendida,
            metodo_pago="EFECTIVO",
            turno=turno
        )

        producto_a_vender.refresh_from_db()
        self.assertEqual(producto_a_vender.stock, stock_inicial - cantidad_vendida)

    def test_vender_producto_sin_stock_falla(self):
        """Prueba que no se puede vender un producto sin stock suficiente."""
        turno = Turno.objects.create(usuario=self.employee_user, tipo_turno=Turno.TipoTurno.DIA)
        producto_a_vender = self.producto
        stock_inicial = producto_a_vender.stock
        cantidad_a_vender = stock_inicial + 1

        with self.assertRaises(ValidationError) as cm:
            vender_producto(
                producto=producto_a_vender,
                cantidad=cantidad_a_vender,
                metodo_pago="EFECTIVO",
                turno=turno
            )

        self.assertIn("Stock insuficiente", cm.exception.messages[0])
        producto_a_vender.refresh_from_db()
        self.assertEqual(producto_a_vender.stock, stock_inicial)  # El stock no debe cambiar
