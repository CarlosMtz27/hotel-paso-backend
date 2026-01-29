from pathlib import Path
import os
from datetime import timedelta

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY no definido en variables de entorno")

CODIGO_ADMIN_INVITADO = os.getenv("CODIGO_ADMIN_INVITADO")

DEBUG = os.getenv("DEBUG", "False") == "True"

ALLOWED_HOSTS = []

INSTALLED_APPS = [
    # Django Core Apps
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Third Party Apps
    "rest_framework",
    'rest_framework_simplejwt.token_blacklist',
    'django_filters',

    # Local apps
    "apps.core.apps.CoreConfig",
    "apps.users.apps.UsersConfig",
    "apps.turnos.apps.TurnosConfig",
    "apps.caja.apps.CajaConfig",
    "apps.estancias.apps.EstanciasConfig",
    "apps.reportes.apps.ReportesConfig",
    "apps.habitaciones.apps.HabitacionesConfig",
    "apps.productos.apps.ProductosConfig",
    "apps.tarifas.apps.TarifasConfig",
]

AUTH_USER_MODEL = "users.Usuario"

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

LANGUAGE_CODE = "es-mx"
TIME_ZONE = "America/Mexico_City"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "mediafiles"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend'
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    'EXCEPTION_HANDLER': 'apps.core.exceptions.custom_exception_handler',

}

SIMPLE_JWT = {
    # --- Duración de los Tokens ---
    # El token que se usa para autenticar cada petición. Vida corta por seguridad.
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=15),
    # El token que permite obtener un nuevo access token. Vida larga para mantener la sesión.
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),

    # --- Rotación de Tokens (Mayor Seguridad) ---
    # Al refrescar, se invalida el refresh token usado y se emite uno nuevo.
    "ROTATE_REFRESH_TOKENS": True,
    # Añade a la lista negra el refresh token usado después de la rotación.
    "BLACKLIST_AFTER_ROTATION": True,

    # --- Configuración Estándar ---
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "VERIFYING_KEY": None,
    "AUDIENCE": None,
    "ISSUER": None,
    "JWK_URL": None,
    "LEEWAY": 0,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "USER_AUTHENTICATION_RULE": "rest_framework_simplejwt.authentication.default_user_authentication_rule",
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_TYPE_CLAIM": "token_type",
    "JTI_CLAIM": "jti",
    "UPDATE_LAST_LOGIN": True,
}
