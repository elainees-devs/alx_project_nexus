import environ
from pathlib import Path
import os
from datetime import timedelta
import dj_database_url


BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(
    DEBUG=(bool, False)  # default DEBUG value
)
env.read_env(BASE_DIR / ".env")  # read .env file

# Detect environment
DJANGO_ENV = env("DJANGO_ENV", default="development")

# -------------------------
# CORS settings
# -------------------------
if DJANGO_ENV == "development":
    # Allow all origins locally
    CORS_ALLOW_ALL_ORIGINS = True
else:
    # Production: restrict origins
    CORS_ALLOW_ALL_ORIGINS = False
    CORS_ALLOWED_ORIGINS = [
        "https://alx-project-nexus-mtwe.onrender.com",
        # Add other allowed origins
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

SECRET_KEY = env("SECRET_KEY")
DEBUG = env("DEBUG")
ALLOWED_HOSTS = ['*']



# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # 3rd party apps
    'rest_framework',
    'django_celery_results',
    'drf_yasg', # for swagger

    # custom apps
    'users',
    'jobs',
    'applications',
    'payments',
    'companies',
    'notifications',
    'rate_limit',
    'request_logs',
    
   
]

# REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,  # default number of items per page
}


SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
}

SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header',
            'description': "JWT Authorization header using the Bearer scheme. Example: 'Bearer <token>'",
        }
    },
}

AUTH_USER_MODEL = 'users.User'
LOGIN_REDIRECT_URL = '/admin/'   # after admin login, go to admin home
LOGOUT_REDIRECT_URL = '/admin/'  # after logout, go to admin home
LOGIN_URL = '/admin/login/'      # where admin should login if unauthenticated


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    
    # custom middleware
    'request_logs.middleware.RequestLoggingMiddleware',
]

ROOT_URLCONF = 'api.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'jobsboard' / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'api.wsgi.application'

# Base URL
BASE_URL = env("BASE_URL") # For local dev


# -------------------------
# Database
# -------------------------
DATABASE_URL = env("DATABASE_URL", default=None)

if DATABASE_URL:
    # Use single DATABASE_URL if provided (e.g., Render)
    DATABASES = {
        "default": dj_database_url.config(default=DATABASE_URL, conn_max_age=600)
    }
else:
    # Fallback: use individual environment variables (local development)
    DATABASES = {
        "default": {
            "ENGINE": env("DATABASE_ENGINE", default="django.db.backends.postgresql"),
            "NAME": env("DATABASE_NAME", default="postgres"),
            "USER": env("DATABASE_USER", default="postgres"),
            "PASSWORD": env("DATABASE_PASSWORD", default="postgres"),
            "HOST": env("DATABASE_HOST", default="localhost"),
            "PORT": env("DATABASE_PORT", default="5432"),
        }
    }


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# HTTPS Security settings
SECURE_SSL_REDIRECT=env("SECURE_SSL_REDIRECT", default=False)
SECURE_HSTS_SECONDS=env("SECURE_HSTS_SECONDS", default=31536000)  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS=env("SECURE_HSTS_INCLUDE_SUBDOMAINS", default=True)
SECURE_HSTS_PRELOAD=env("SECURE_HSTS_PRELOAD", default=True)

# Secure cookies
SESSION_COOKIE_SECURE=env("SESSION_COOKIE_SECURE", default=False)
CSRF_COOKIE_SECURE=env("CSRF_COOKIE_SECURE", default=False)
SESSION_COOKIE_HTTPONLY=env("SESSION_COOKIE_HTTPONLY", default=True)
CSRF_COOKIE_HTTPONLY=env("CSRF_COOKIE_HTTPONLY", default=False)  # keep False unless you never use AJAX forms



# -----------------------
# Email settings
# -----------------------
EMAIL_BACKEND = env("EMAIL_BACKEND").strip()
EMAIL_HOST = env("EMAIL_HOST").strip()
EMAIL_PORT = env.int("EMAIL_PORT")
EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS")
EMAIL_HOST_USER = env("EMAIL_HOST_USER").strip()
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD").strip()
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL").strip()

# -----------------------
# Celery
# -----------------------
CELERY_BROKER_URL = env.str("CELERY_BROKER_URL",default="redis://localhost:6379/0")
CELERY_RESULT_BACKEND = env("CELERY_RESULT_BACKEND")
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "Africa/Nairobi"


# Optional: retry configuration
CELERY_TASK_ACKS_LATE = True
CELERY_WORKER_PREFETCH_MULTIPLIER = 1

# Chapa Secret key
CHAPA_SECRET_KEY = env("CHAPA_SECRET_KEY")

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = "Africa/Nairobi"
USE_I18N = True
USE_TZ = True


# Logging configuration
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {"class": "logging.StreamHandler"},
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
}


# Static files (CSS, JavaScript, Images)
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"


# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
