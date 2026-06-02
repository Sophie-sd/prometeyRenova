from pathlib import Path
import os
from dotenv import load_dotenv
from django.urls import reverse_lazy

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-CHANGE-IN-PRODUCTION')
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

# ALLOWED_HOSTS
ALLOWED_HOSTS = ['www.prometeylabs.com', 'prometeylabs.com']

RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.extend([RENDER_EXTERNAL_HOSTNAME, f'www.{RENDER_EXTERNAL_HOSTNAME}'])

if DEBUG:
    ALLOWED_HOSTS.extend(['localhost', '127.0.0.1', '0.0.0.0', '127.0.0.1:8000', 'localhost:8000', 'testserver', '*'])

# APPS
INSTALLED_APPS = [
    # Unfold — ЗАВЖДИ перед django.contrib.admin
    "unfold",
    "unfold.contrib.filters",

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'apps.core',
    'apps.blog',
    'apps.payment',
]

# UNFOLD ADMIN
UNFOLD = {
    "SITE_TITLE": "Prometey Labs",
    "SITE_HEADER": "Prometey Labs — Адмінпанель",
    "COLORS": {
        "primary": {
            "50":  "255 247 237",
            "100": "255 237 213",
            "200": "254 215 170",
            "300": "253 186 116",
            "400": "251 146 60",
            "500": "249 115 22",
            "600": "234 88 12",
            "700": "194 65 12",
            "800": "154 52 18",
            "900": "124 45 18",
            "950": "67 20 7",
        },
    },
    "SCRIPTS": ["admin/js/admin-theme.js"],
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": False,
        "navigation": [
            {
                "title": "CRM — Заявки",
                "items": [
                    {"title": "Нові заявки", "icon": "inbox",        "link": reverse_lazy("admin:core_formsubmission_changelist")},
                    {"title": "В роботі",    "icon": "engineering",  "link": reverse_lazy("admin:core_inprogressformsubmission_changelist")},
                    {"title": "Завершено",   "icon": "check_circle", "link": reverse_lazy("admin:core_completedformsubmission_changelist")},
                    {"title": "Архів",       "icon": "archive",      "link": reverse_lazy("admin:core_archivedformsubmission_changelist")},
                ],
            },
            {
                "title": "Платежі",
                "separator": True,
                "items": [
                    {"title": "Посилання",     "icon": "link",            "link": reverse_lazy("admin:payment_paymentlink_changelist")},
                    {"title": "Отримувачі",   "icon": "account_balance", "link": reverse_lazy("admin:payment_recipientprofile_changelist")},
                    {"title": "Налаштування", "icon": "settings",        "link": reverse_lazy("admin:payment_paymentsettings_changelist")},
                ],
            },
            {
                "title": "Блог",
                "separator": True,
                "items": [
                    {"title": "Статті", "icon": "article", "link": reverse_lazy("admin:blog_blogpost_changelist")},
                ],
            },
            {
                "title": "Система",
                "separator": True,
                "items": [
                    {"title": "Користувачі", "icon": "person", "link": reverse_lazy("admin:auth_user_changelist")},
                ],
            },
        ],
    },
}

# MIDDLEWARE
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'apps.core.middleware.CSPMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Додаємо no-cache middleware для розробки
if DEBUG:
    MIDDLEWARE.append('prometey_project.middleware.NoCacheMiddleware')

ROOT_URLCONF = 'config.urls'
WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'

# DATABASE - PostgreSQL для Render, SQLite для локальної розробки
import dj_database_url

DATABASE_URL = os.environ.get('DATABASE_URL')

if DATABASE_URL:
    # Продакшн (Render) - PostgreSQL
    DATABASES = {
        'default': dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
else:
    # Локальна розробка - SQLite
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# INTERNATIONALIZATION - Мультимовність
LANGUAGE_CODE = 'uk'
LANGUAGES = [
    ('uk', 'Українська'),
    ('en', 'English'),
    ('ru', 'Русский'),
]
LOCALE_PATHS = [os.path.join(BASE_DIR, 'locale')]
TIME_ZONE = 'Europe/Kyiv'
USE_I18N = True
USE_TZ = True

# STATIC & MEDIA
STATIC_URL = '/static/'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# WhiteNoise налаштування
if DEBUG:
    STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
else:
    # Продакшн: WhiteNoise з gzip/brotli компресією CSS/JS під час collectstatic
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'
    WHITENOISE_MAX_AGE = 31536000
    WHITENOISE_SKIP_COMPRESS_EXTENSIONS = ['jpg', 'jpeg', 'png', 'gif', 'webp', 'zip', 'gz', 'bz2']
    WHITENOISE_IMMUTABLE_FILE_TEST = lambda path, url: url.startswith('/static/') and ('.' in url)

# TEMPLATES
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.i18n',
                'django.template.context_processors.csrf',
                'apps.core.context_processors.global_settings',
            ],
        },
    },
]

# EMAIL
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', 'your-email@gmail.com')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', 'your-password')
EMAIL_TIMEOUT = 10  # Максимум 10 секунд для email операцій

# MAILGUN
ANYMAIL = {
    "MAILGUN_API_KEY": os.environ.get('MAILGUN_API_KEY', ''),
    "MAILGUN_SENDER_DOMAIN": os.environ.get('MAILGUN_DOMAIN', 'mg.prometeylabs.com'),
}

DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'Prometey Labs <prometeylabs@gmail.com>')
CONTACT_EMAIL = os.environ.get('CONTACT_EMAIL', 'prometeylabs@gmail.com')

# MONOBANK - Зберігаємо поточні налаштування
MONOBANK_TOKEN = os.environ.get('MONOBANK_TOKEN', '')
SITE_URL = os.environ.get('SITE_URL', 'https://www.prometeylabs.com')
if DEBUG:
    SITE_URL = os.environ.get('SITE_URL', 'http://localhost:8000')

# FACEBOOK PIXEL
FACEBOOK_PIXEL_ID = os.environ.get('FACEBOOK_PIXEL_ID', '1991082531458369')

# KEYCRM
KEYCRM_API_KEY = os.environ.get('KEYCRM_API_KEY', '')
KEYCRM_PIPELINE_ID = int(os.environ.get('KEYCRM_PIPELINE_ID', '1'))
# Загальний fallback source_id для заявок без платних UTM і без лендінгових ознак
# (форми з головної, footer, контактів тощо).
KEYCRM_SOURCE_ID = os.environ.get('KEYCRM_SOURCE_ID', '')
KEYCRM_GCLID_FIELD_UUID = os.environ.get('KEYCRM_GCLID_FIELD_UUID', '')
KEYCRM_WEBHOOK_SECRET = os.environ.get('KEYCRM_WEBHOOK_SECRET', '')
KEYCRM_SUCCESS_STATUS_ID = os.environ.get('KEYCRM_SUCCESS_STATUS_ID', '')

# KEYCRM — розподіл джерел: платний Google Ads vs органіка з лендінгів.
# Числові ID джерел з KeyCRM (Налаштування → Джерела). Якщо ID не задано —
# resolver використає наступний у пріоритеті або загальний KEYCRM_SOURCE_ID.
KEYCRM_SOURCE_PAID_SHOPS = os.environ.get('KEYCRM_SOURCE_PAID_SHOPS', '')
KEYCRM_SOURCE_PAID_CORPORATE = os.environ.get('KEYCRM_SOURCE_PAID_CORPORATE', '')
KEYCRM_SOURCE_PAID_ALL = os.environ.get('KEYCRM_SOURCE_PAID_ALL', '')
KEYCRM_SOURCE_ORGANIC_SHOPS = os.environ.get('KEYCRM_SOURCE_ORGANIC_SHOPS', '')
KEYCRM_SOURCE_ORGANIC_CORPORATE = os.environ.get('KEYCRM_SOURCE_ORGANIC_CORPORATE', '')

# Підрядки для зіставлення utm_campaign з потрібним джерелом (через кому, case-insensitive).
# Перевірка йде в порядку: Corporate → Shops → All (щоб уникнути колізій,
# наприклад коли utm_campaign містить і "shops" і "corporate" одночасно).
KEYCRM_UTM_MATCH_PAID_CORPORATE = os.environ.get('KEYCRM_UTM_MATCH_PAID_CORPORATE', '')
KEYCRM_UTM_MATCH_PAID_SHOPS = os.environ.get('KEYCRM_UTM_MATCH_PAID_SHOPS', '')
KEYCRM_UTM_MATCH_PAID_ALL = os.environ.get('KEYCRM_UTM_MATCH_PAID_ALL', '')

# GOOGLE ADS API
GOOGLE_ADS_DEVELOPER_TOKEN = os.environ.get('GOOGLE_ADS_DEVELOPER_TOKEN', '')
GOOGLE_ADS_CLIENT_ID = os.environ.get('GOOGLE_ADS_CLIENT_ID', '')
GOOGLE_ADS_CLIENT_SECRET = os.environ.get('GOOGLE_ADS_CLIENT_SECRET', '')
GOOGLE_ADS_REFRESH_TOKEN = os.environ.get('GOOGLE_ADS_REFRESH_TOKEN', '')
GOOGLE_ADS_CUSTOMER_ID = os.environ.get('GOOGLE_ADS_CUSTOMER_ID', '')
GOOGLE_ADS_LOGIN_CUSTOMER_ID = os.environ.get('GOOGLE_ADS_LOGIN_CUSTOMER_ID', '')
GOOGLE_ADS_CONVERSION_ACTION_ID = os.environ.get('GOOGLE_ADS_CONVERSION_ACTION_ID', '')

# CSRF налаштування - ВИПРАВЛЕНО
# Завжди включаємо основні домени
CSRF_TRUSTED_ORIGINS = [
    'https://www.prometeylabs.com',
    'https://prometeylabs.com',
]

# Додаємо динамічний RENDER URL якщо є
RENDER_EXTERNAL_URL = os.environ.get('RENDER_EXTERNAL_URL', '').rstrip('/')
if RENDER_EXTERNAL_URL:
    from urllib.parse import urlparse
    parsed = urlparse(RENDER_EXTERNAL_URL)
    origin = f"{parsed.scheme}://{parsed.netloc}" if parsed.scheme and parsed.netloc else RENDER_EXTERNAL_URL
    if origin not in CSRF_TRUSTED_ORIGINS:
        CSRF_TRUSTED_ORIGINS.append(origin)
    host = parsed.netloc or origin.replace('https://', '').replace('http://', '')
    if host and host not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append(host)

# Для локальної розробки
if DEBUG:
    CSRF_TRUSTED_ORIGINS.extend([
        'http://localhost:8000',
        'http://localhost:8001', 
        'http://127.0.0.1:8000',
        'http://127.0.0.1:8001',
        'http://0.0.0.0:8000'
    ])

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
    SECURE_SSL_REDIRECT = os.environ.get('SECURE_SSL_REDIRECT', 'False') == 'True'

# LOGGING
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
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
        'apps': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'apps.core.keycrm_service': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'apps.core.google_ads_service': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'apps.core.webhooks': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    }
}

if DEBUG:
    LOGGING['handlers']['file'] = {
        'level': 'INFO',
        'class': 'logging.FileHandler',
        'filename': os.path.join(BASE_DIR, 'debug.log'),
        'formatter': 'verbose',
    }
    for logger in ['django', 'apps']:
        LOGGING['loggers'][logger]['handlers'].append('file')
        LOGGING['loggers'][logger]['level'] = 'DEBUG'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'