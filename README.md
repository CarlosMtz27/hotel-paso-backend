# Hotel Paso - Backend API

Este repositorio contiene el backend para el sistema de gestión "Hotel Paso". Es una API RESTful construida con **Django** y **Django Rest Framework (DRF)**, diseñada para administrar la operación de un hotel/motel, con un fuerte enfoque en el control de caja, turnos de empleados y gestión de estancias por horas.

## Características Principales

### 1. Gestión de Usuarios y Autenticación (`apps.users`)
*   **Roles:** Sistema basado en roles: `ADMINISTRADOR`, `EMPLEADO` e `INVITADO`.
*   **JWT:** Autenticación segura mediante JSON Web Tokens (SimpleJWT).
*   **Login de Invitado:** Funcionalidad especial para crear usuarios temporales sin contraseña para accesos rápidos o modo kiosco.
*   **Seguridad:** Los usuarios inactivos son bloqueados automáticamente en el login.

### 2. Control de Turnos (`apps.turnos`)
*   **Apertura y Cierre:** Lógica transaccional para iniciar y cerrar turnos.
*   **Reglas de Negocio:**
    *   Un usuario no puede tener más de un turno activo.
    *   Validación de caja inicial y final.
*   **Arqueo de Caja:** Cálculo automático de `efectivo_esperado` vs `efectivo_reportado` al cerrar el turno para detectar diferencias (sobrantes/faltantes).
*   **Resumen:** Generación de reportes resumidos al cierre (total efectivo, transferencias, tarjetas).

### 3. Caja y Movimientos (`apps.caja`)
*   **Trazabilidad:** Cada movimiento de dinero (ingreso) está vinculado estrictamente a un `Turno` activo.
*   **Tipos de Movimiento:**
    *   `ESTANCIA`: Cobro por alquiler de habitación.
    *   `PRODUCTO`: Venta de artículos del minibar/recepción.
    *   `EXTRA`: Cobro por horas adicionales.
*   **Atomicidad:** Las ventas y cobros se ejecutan dentro de transacciones atómicas para asegurar la integridad financiera.

### 4. Gestión de Estancias (`apps.estancias`)
*   **Ciclo de Vida:** Apertura (Check-in), Extensión de tiempo y Cierre (Check-out).
*   **Tarifas:** Cálculo automático de la hora de salida basado en la tarifa seleccionada (ej. 3 horas, 12 horas).
*   **Continuidad:** Soporte para cerrar una estancia en un turno diferente al que se abrió.

### 5. Ventas de Productos (`apps.caja` + `apps.productos`)
*   Control de stock en tiempo real al realizar una venta.
*   Validación de productos activos.

## Tecnologías

*   **Lenguaje:** Python 3.x
*   **Framework Web:** Django
*   **API:** Django Rest Framework
*   **Autenticación:** djangorestframework-simplejwt
*   **Base de Datos:** (Configurable, por defecto SQLite/PostgreSQL según `settings.py`)

## Instalación y Configuración

1.  **Clonar el repositorio:**
    ```bash
    git clone https://github.com/CarlosMtz27/hotel-paso-backend.git
    cd hotel-paso-backend
    ```

2.  **Crear un entorno virtual:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # En Windows: venv\Scripts\activate
    ```

3.  **Instalar dependencias:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Aplicar migraciones:**
    ```bash
    python manage.py migrate
    ```

5.  **Crear un superusuario:**
    ```bash
    python manage.py createsuperuser
    ```

6.  **Ejecutar el servidor:**
    ```bash
    python manage.py runserver
    ```

## Endpoints Principales

### Autenticación
*   `POST /api/token/`: Obtener par de tokens (Access + Refresh).
*   `POST /api/users/login-invitado/`: Login rápido para invitados.
*   `POST /api/users/logout/`: Invalidar refresh token.

### Turnos
*   `POST /api/turnos/iniciar/`: Abrir un nuevo turno.
*   `POST /api/turnos/cerrar/`: Cerrar turno actual y reportar efectivo.
*   `GET /api/turnos/activo/`: Obtener el turno activo del usuario.

### Estancias
*   `POST /api/estancias/abrir/`: Check-in.
*   `POST /api/estancias/cerrar/`: Check-out.
*   `POST /api/estancias/agregar-horas/`: Extender estancia.


