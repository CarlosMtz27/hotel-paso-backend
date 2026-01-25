from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.users.models import Usuario
from .models import Producto


class ProductoAPITests(APITestCase):
    def setUp(self):
        # Crear usuarios con diferentes roles
        self.admin_user = Usuario.objects.create_user(username='admin', password='password123', rol=Usuario.Rol.ADMINISTRADOR)
        self.employee_user = Usuario.objects.create_user(username='employee', password='password123', rol=Usuario.Rol.EMPLEADO)

        # Crear un producto de prueba
        self.producto = Producto.objects.create(nombre="Agua Mineral", precio=100.00)

        # URLs
        self.list_create_url = reverse('productos_list')
        self.detail_url = reverse('productos_detail', kwargs={'pk': self.producto.pk})

    def test_admin_puede_crear_producto(self):
        """Prueba que un administrador puede crear un producto."""
        self.client.force_authenticate(user=self.admin_user)
        data = {'nombre': 'Jugo de Naranja', 'precio': '120.50'}
        response = self.client.post(self.list_create_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Producto.objects.count(), 2)

    def test_empleado_no_puede_crear_producto(self):
        """Prueba que un empleado no puede crear un producto."""
        self.client.force_authenticate(user=self.employee_user)
        data = {'nombre': 'Jugo de Naranja', 'precio': '120.50'}
        response = self.client.post(self.list_create_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_puede_actualizar_producto(self):
        """Prueba que un administrador puede actualizar un producto."""
        self.client.force_authenticate(user=self.admin_user)
        data = {'nombre': 'Agua con Gas', 'precio': '110.00', 'activo': False}
        response = self.client.put(self.detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.nombre, 'Agua con Gas')
        self.assertFalse(self.producto.activo)

    def test_empleado_no_puede_actualizar_producto(self):
        """Prueba que un empleado no puede actualizar un producto."""
        self.client.force_authenticate(user=self.employee_user)
        data = {'nombre': 'Agua con Gas', 'precio': '110.00'}
        response = self.client.put(self.detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_crear_producto_duplicado_falla_api(self):
        """Prueba que la API no permite crear productos con el mismo nombre."""
        self.client.force_authenticate(user=self.admin_user)
        data = {'nombre': 'Agua Mineral', 'precio': '150.00'}  # 'Agua Mineral' ya existe
        response = self.client.post(self.list_create_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['nombre'][0], 'Ya existe un producto con ese nombre.')

    def test_crear_producto_precio_invalido_falla_api(self):
        """Prueba que la API no permite crear productos con precio cero o negativo."""
        self.client.force_authenticate(user=self.admin_user)
        data = {'nombre': 'Nuevo Producto', 'precio': '0.00'}
        response = self.client.post(self.list_create_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['precio'][0], 'El precio debe ser mayor a cero.')
