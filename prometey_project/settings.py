"""
Django settings for prometey_project - Оптимізовано
"""
import os
from urllib.parse import urlparse
from .settings_base import *  # Базові налаштування

# === ENVIRONMENT SPECIFIC SETTINGS ===

# Hosts
ALLOWED_HOSTS = [h for h in os.getenv('ALLOWED_HOSTS', '').split(',') if h] if not DEBUG else ['localhost', '127.0.0.1', '0.0.0.0', '*']

# Middleware для розробки
if DEBUG:
    MIDDLEWARE.append('prometey_project.middleware.NoCacheMiddleware')

# === DATABASE CONFIGURATION ===

if not DEBUG:
    # Продакшн - PostgreSQL на Render
    DATABASE_URL = os.getenv('DATABASE_URL', '')
    if DATABASE_URL:
        import dj_database_url  # Імпорт всередині if блоку для продакшн
        DATABASES = {
            'default': dj_database_url.parse(
                DATABASE_URL, 
                conn_max_age=600, 
                ssl_require=True,
                conn_health_checks=True
            )
        }
    else:
        # Fallback до SQLite якщо DATABASE_URL не встановлена
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': BASE_DIR / 'db.sqlite3',
            }
        }
else:
    # Розробка - SQLite
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# === STATIC FILES CONFIGURATION ===

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

if DEBUG:
    # Розробка - прості налаштування
    STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
    STATICFILES_FINDERS = [
        'django.contrib.staticfiles.finders.FileSystemFinder',
        'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    ]
else:
    # Продакшн - WhiteNoise для статики
    MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
    WHITENOISE_USE_FINDERS = True
    WHITENOISE_ROOT = STATIC_ROOT
    WHITENOISE_MAX_AGE = 31536000
    WHITENOISE_INDEX_FILE = True

# === SECURITY CONFIGURATION ===

# CSRF налаштування
RENDER_EXTERNAL_URL = os.getenv('RENDER_EXTERNAL_URL', '').rstrip('/')
if RENDER_EXTERNAL_URL:
    parsed = urlparse(RENDER_EXTERNAL_URL)
    origin = f"{parsed.scheme}://{parsed.netloc}" if parsed.scheme and parsed.netloc else RENDER_EXTERNAL_URL
    CSRF_TRUSTED_ORIGINS = [origin]
    host = parsed.netloc or origin.replace('https://', '').replace('http://', '')
    if host and host not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append(host)
else:
    CSRF_TRUSTED_ORIGINS = ['http://localhost:8000', 'http://127.0.0.1:8000', 'http://0.0.0.0:8000']

# Security headers (тільки для продакшн)
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_SSL_REDIRECT = os.getenv('SECURE_SSL_REDIRECT', 'False') == 'True'

# === EMAIL CONFIGURATION ===

# Налаштування для розробки/продакшн
if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
else:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
    EMAIL_PORT = int(os.getenv('EMAIL_PORT', '587'))
    EMAIL_USE_TLS = True
    EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
    EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')

# === LOGGING CONFIGURATION ===

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        # Логування для додатків
        'apps': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
