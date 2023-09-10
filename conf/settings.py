"""
Propietario: grIT
Contacto: agustin.gomez.mansilla@gmail.com

Use of this code for any commercial purpose is NOT AUTHORIZED.
El uso de éste código para cualquier propósito comercial NO ESTÁ AUTORIZADO.
"""

from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

AUTH_USER_MODEL = 'eventos.Usuario'

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', False)

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS').split(',')


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.sitemaps',
    'django.contrib.staticfiles',
    'eventos',
    'api'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'conf.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates'],
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

#Email settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_USE_SSL = True
EMAIL_HOST = os.environ.get('MAIL_HST', '')
EMAIL_HOST_USER = os.environ.get('MAIL_USR', '')
EMAIL_HOST_PASSWORD = os.environ.get('MAIL_PWD', '')
EMAIL_PORT = os.environ.get('MAIL_PRT', '')

DEFAULT_FROM_EMAIL = 'Ejumina <{}>'.format(os.environ.get('MAIL_USR', ''))

WSGI_APPLICATION = 'conf.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

if os.environ.get('DB_ENGINE', 'SQLITE3') == 'MYSQL':
    engine = {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('DB_SCHEMA'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PWD'),
        'HOST': os.getenv('DB_HOST'),
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'"
        }
    }
else:
    engine = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
    options = {}
DATABASES = {
    'default': engine
}


CSRF_COOKIE_SECURE = True
CSRF_USE_SESSIONS = True
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_NAME = '__Secure-sessionid'
CSRF_COOKIE_NAME = '__Secure-csrftoken'
ROOT_URLCONF = 'conf.urls'
CSRF_COOKIE_HTTPONLY = True
CSRF_FAILURE_VIEW = 'eventos.views.errors.csrf_fail'
SESSION_COOKIE_SAMESITE = 'Lax'

# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = 'es'

TIME_ZONE = 'America/Asuncion'

USE_I18N = True
USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_URL = os.getenv('STATIC_URL')
STATIC_ROOT = os.getenv('STATIC_ROOT')
MEDIA_ROOT = os.path.join(BASE_DIR, os.getenv('MEDIA_ROOT'))
MEDIA_URL = os.getenv('MEDIA_URL')

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


LOGOUT_REDIRECT_URL = '/'
X_FRAME_OPTIONS = 'DENY'

if os.getenv('DEBUG'):
    SECURE_CONTENT_TYPE_NOSNIFF = False
    SECURE_HSTS_SECONDS = 15768000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = False
    SECURE_HSTS_PRELOAD = False
    SECURE_SSL_REDIRECT = False
else:
    SECURE_CONTENT_TYPE_NOSNIFF = True
    ## Strict-Transport-Security
    SECURE_HSTS_SECONDS = 15768000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_SSL_REDIRECT = True



CSP_REPORT_URI = '<add your reporting uri>'


# default source as self
CSP_DEFAULT_SRC = ("'none'",)

# style from our domain and bootstrapcdn
CSP_STYLE_SRC = ("'self'",
                 "cdn.jsdelivr.net",
                 "www.google.com",
                 os.getenv('STATIC_URL'))

# scripts from our domain and other domains
CSP_SCRIPT_SRC = ("'self'",
                  "ajax.googleapis.com",
                  "https://www.google.com/recaptcha/",
                  "https://www.gstatic.com/recaptcha/",
                  os.getenv('STATIC_URL')
                 )

CSP_FRAME_SRC = ("https://www.google.com/recaptcha/")

# images from our domain and other domains
CSP_IMG_SRC = ("'self'",
               os.getenv('STATIC_URL'),
               os.getenv('MEDIA_URL'))

# loading manifest, workers, frames, etc
CSP_FONT_SRC = ("'self'", "cdn.jsdelivr.net", os.getenv('STATIC_URL'))
CSP_CONNECT_SRC = ("'self'",)
CSP_OBJECT_SRC = ("'self'",)
CSP_BASE_URI = ("'self'",)
CSP_FRAME_ANCESTORS = ("'self'",)
CSP_FORM_ACTION = ("'self'",)
CSP_INCLUDE_NONCE_IN = ('script-src', 'style-src')
CSP_MANIFEST_SRC = ("'self'",)
CSP_WORKER_SRC = ("'self'",)
CSP_MEDIA_SRC = ("'self'",)

CSP_REPORT_PERCENTAGE = 0.1
