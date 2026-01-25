from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.core.exceptions import ValidationError

from apps.users.models import Usuario
from .models import Producto
from .services import crear_producto


class ProductoServiceTests(APITestCase):
    def test_crear_producto_exitoso(self):
        """Prueba que el servicio crea un producto correctamente."""
        producto = crear_producto(nombre="Gaseosa", precio=150.00)
        self.assertEqual(Producto.objects.count(), 1)
        self.assertEqual(producto.nombre, "Gaseosa")

    def test_crear_producto_duplicado_falla(self):
        """Prueba que el servicio no permite crear productos con el mismo nombre."""
        crear_producto(nombre="Gaseosa", precio=150.00)
        with self.assertRaisesMessage(ValidationError, "Ya existe un producto con ese nombre."):
            crear_producto(nombre="Gaseosa", precio=200.00)


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
