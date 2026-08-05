import os
from pathlib import Path
import dj_database_url

# 1. BASE DIRECTORY
BASE_DIR = Path(__file__).resolve().parent.parent

# 2. SECURITY CONFIGURATIONS
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'fbchw3&+vaut7yj4c9$jz$a=9r40d-zp&=be32@5hu_+wi1=zh')
DEBUG = os.environ.get('DJANGO_DEBUG', 'True') == 'True'

ALLOWED_HOSTS = os.environ.get(
    'ALLOWED_HOSTS',
    'busfermata.onrender.com,wedehagertransport.onrender.com,localhost,127.0.0.1'
).split(',')

# HTTPS & Cookie Security Options
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

# 3. APPLICATION DEFINITION
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third Party Apps
    'rest_framework',
    'drf_spectacular',
    'corsheaders',
    'axes',
    'turnstile', 

    # Project Apps
    'users',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'axes.middleware.AxesMiddleware',
]

ROOT_URLCONF = 'myproje.urls'
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',  # እዚህ ጋር በትክክል ተጻፉን ያረጋግጡ
        'DIRS': [BASE_DIR / 'users' / 'templates'],
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

"""
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.DjangoTemplates',
        'DIRS': [BASE_DIR / 'users' / 'templates'],
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
"""


WSGI_APPLICATION = 'myproje.wsgi.application'

# 4. DATABASE CONFIGURATION
DATABASES = {
    'default': dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600,
        ssl_require=not DEBUG
    )
}

# 5. AUTHENTICATION & USERS
AUTH_USER_MODEL = 'users.CustomUser'
AUTHENTICATION_BACKENDS = [
    'axes.backends.AxesStandaloneBackend',
    'django.contrib.auth.backends.ModelBackend',
]

AXES_ENABLED = os.environ.get('AXES_ENABLED', 'False') == 'True'

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'hibir-auth-ratelimit-protector',
    }
}

TURNSTILE_SITE_KEY = os.environ.get('TURNSTILE_SITE_KEY', '0x4AAAAAAAM1_xxxxxxxxxxxx')
TURNSTILE_SECRET_KEY = os.environ.get('TURNSTILE_SECRET_KEY', '0x4AAAAAAAM1_xxxxxxxxxxxx')

# 6. EMAIL SETTINGS
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', 'teklemariammossie1@gmail.com')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', 'xbbdaymgoqapntds')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'teklemariammossie697@gmail.com')

# 7. STATIC & MEDIA FILES
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'users' / 'static']

#STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
STATICFILES_STORAGE = "whitenoise.storage.CompressedStaticFilesStorage"

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# 8. CORS & CSRF CONFIGURATIONS
CORS_ALLOW_ALL_ORIGINS = True

CSRF_TRUSTED_ORIGINS = [
    'https://wedehagertransport.onrender.com',
    'https://busfermata.onrender.com'
]

# 9. INTERNATIONALIZATION
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Addis_Ababa'
USE_I18N = True
USE_TZ = True
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# 10. REST FRAMEWORK & SPECTACULAR
REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ],
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'Busfermata Digital Technology API',
    'DESCRIPTION': 'Cross-Country Bus Fleet Management & Electronic Ticketing API Documentation',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}

# 11. TELEBIRR PAYMENT & TRANSIT SYNC INTEGRATION
TELEBIRR_CONFIG = {
    # /payment/v1 በ views.py ውስጥ ስለሚጨመር እዚህ ጋር የመጨረሻው ድግግሞሽ እንዳይፈጠር ተስተካክሏል
    'BASE_URL': os.environ.get(
        'TELEBIRR_BASE_URL',
        'https://app.ethiotelecom.et:10443'
    ),
    'WEB_BASE_URL': os.environ.get(
        'TELEBIRR_WEB_BASE_URL',
        'https://app.ethiotelecom.et:10443/'
    ),
    'merchantCode': os.environ.get('TELEBIRR_MERCHANT_CODE', '259159'),
    'merchantAppId': os.environ.get('TELEBIRR_MERCHANT_APP_ID', '167418508741200'),
    'fabricAppId': os.environ.get('TELEBIRR_FABRIC_APP_ID', 'c4182ef8-9249-458e-985e-06d191f4d505'),
    'appSecret': os.environ.get('TELEBIRR_APP_SECRET', 'fad0f06383c6297f545876694b9745545876694b9745'),
    'notify_url': os.environ.get(
        'TELEBIRR_NOTIFY_URL',
        'https://busfermata.onrender.com/users/telebirr/notify/'
    ),
    'redirect_url': os.environ.get(
        'TELEBIRR_REDIRECT_URL',
        'https://busfermata.onrender.com/payment-success/'
    ),
    'PRIVATE_KEY': os.environ.get(
        'TELEBIRR_PRIVATE_KEY',
        """-----BEGIN PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDd/n5B46RXsS/1
19cgddqxPhieaRh09ZwkrbdMJ3ncgUderWVcC5PHqu9JYme7Y4REajrqBnAxn3sbV
kJghqw7AY1b8uUh2z+X/76mU1rBsaQkHL/JfE6emiyXQ6ROc1TmExXhHnkOL7rAy
IEWNq1rj/n4N99q0PnZTBCFUwEDTdHhtAlu/ti280TbzdWQWIe8Iz3GX/DZsUGtL
/0AIXyEx4/0+kJwVtzxdoAqJRiyGp3xTvzBajUAXGXoBFh96BDoMRwnVzTEiqDfo
EKmUGSkOy83YJO2Fhi553q8SxrBXZwIUm82pxC1yLLqKi6lKBoBptTdHTQTUbE7k
5Ozv5fdRAgMBAAECggEAANu0jH1Sty70gp8/hOIMRY53ruFD4qPGXFe/kBM/Ohfw
IG9HvVoqz96HzGMpc8+eIAfCvL2fZ5ITAXnEYluDfWqhGps9AaQKRRMkP1RbA4XW
+TSfdZ4c8fBIO/McOAmrOp88GluGEKqfHYGLq7LR3fCtnl3iO4Jo/Nk5gHmjqcYD
rclhrLnIvwUheRgXmLSLdksBII5n0nHueJRbBEjZ7YGaa3qaB7AwhgJML1e1+3pn
GWUwMbNMX8jzTLYMhz7oNkG6TD/3oLS1l2LXkovuo4KZuuMxfrf/dGZWiVnUrD6+
+Zuy+l9kYh+0OtAxs7fCJSP1cJ50lyIbMoIvfhFkHwKBgQD25tzkIiQfYQFkjW18
nZ0RcuZnSoh7a9kcwI8RGcqZk5cGGW6FKGz/ICVzD9Kw+QRGwcvV2ypET5vtkP2i
yMGpzRpKbHqMPY8eirzk43UWozehNiqSbIn0erWJrUkELCNCKEAsJLU4lLf4ovMw
JbrTDLlvHG+6eSs1wwEnlr724wKBgQDmLKorMAAkKzbWqrKzZmT/TF1XxtsNLNjr
0FRTYQJHH0rob9sChSacHsG7XV4s9A+p60t594MjaLcvOTUXzusJAQ/PeNg3yxyv
rCm90ud+/EUYNtU1p+4eqBcZq+qeLYwa4NytqpDivR7gKA5BWbCkVDjAwlv4VrJ8
YNvMSOx7OwKBgFIIzNXj3hqq8XqGXx1rhPd6NMGXCxfu8nlSJXbqGd3DIwe8xXLq
xqRR+v9q/3cblecoluBcbIO767QYW52NlIMliZm2x1T3UykzsaVfSdUWr/IZfDWg
aInZh53R/JOtUp21n/TK0YeWKjYrdh/GOXfMH4SibyEHB2taenS76oE/AoGAEvnd
sZ/Mcy7o33vFLcskSnPmQiVPy99FpvNO8GzP/kMTLuSB3sxRaY+TkznYWMZqQCz4
1P5V3mZ0q70ApozVjbF7tzQUR01EeSstacvob+ymWZ+zpi/JDtf2x5QHzLCem1ys
dNjaBwdmcz56JmMZkAKthx6+7FNhdaWamVXtwR8CgYEA56QUe6bgNhcbjyaAAKie
vU/qwYmc/A7D1N0rtlBUNdcfCNBhYX8XeBy3jY4e6t2AyT1LdPkbkdlb95A/KBGP
ncowwp+BlnBfCRwHd0wFuuKyYQNltIbFOjPXcmvV30KZd9mri0HL9x+EnrajuAH3
fR/6nV5MOfLiZ05XSiQXzGs=
-----END PRIVATE KEY-----"""
    )
}

# Ticketing System Synchronization Settings
TELEBIRR_API_KEY = os.environ.get('TELEBIRR_API_KEY', '4F10EF34-DE37-4240-B1BF-A8FEAD615AE3')
TELEBIRR_USERNAME = os.environ.get('TELEBIRR_USERNAME', '61F4AF42-25FF-4B3B-8092-356321979E08')
TELEBIRR_APP_ID = int(os.environ.get('TELEBIRR_APP_ID', 5))
TELEBIRR_AGENT_ID = int(os.environ.get('TELEBIRR_AGENT_ID', 42))
TELEBIRR_TICKETING_BASE_URL = os.environ.get('TELEBIRR_TICKETING_BASE_URL', 'http://196.189.126.8:8010')
