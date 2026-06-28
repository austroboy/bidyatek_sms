import os
from pathlib import Path
from datetime import timedelta
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-^o$=61+v7v^q$uylk44k0j9(1a4z(i8%(fi4bd_%-ffz%01#!z'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True



ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'school.localhost', 'school.localhost:8000']


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG',
    },
}

CORS_ALLOWED_ORIGINS = [
    'http://easydr.xyz',
]

CORS_ALLOW_HEADERS = [
    'Accept',
    'Accept-Language',
    'Authorization',
    'Content-Type',
]
CORS_ALLOW_METHODS = [
    'GET',
    'POST',
    'PUT',
    'DELETE',
]

# Application definition

SHARED_APPS = [
    'django_tenants',
    'organizer',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'shared',
]

TENANT_APPS= [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'django_filters',
    'rest_framework_simplejwt',
    'corsheaders',
    'import_export',
    'widget_tweaks',
    'colorfield',
    'shared',
    'core',
    'user',
    'crucial',
    'exam',
    'miscellaneous',
    'attendance',
    'webpage',
    'accounting',
    'ssl_commerz',
    'django.contrib.humanize',
    'chat',
    'channels',
    'budget',
    ]

INSTALLED_APPS= SHARED_APPS +  [ app for app in TENANT_APPS if app not in SHARED_APPS ]

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
    ]
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=30),  
    'REFRESH_TOKEN_LIFETIME': timedelta(days=365*10), 
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_OBTAIN_SERIALIZER': 'path.to.CustomTokenObtainPairSerializer',
}

MIDDLEWARE = [
    'django_tenants.middleware.main.TenantMainMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    "corsheaders.middleware.CorsMiddleware",
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'sms.urls'
PUBLIC_SCHEMA_URLCONF = 'sms.urls_public'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, "templates")],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'miscellaneous.context_processors.institute_context',
                'miscellaneous.context_processors.sms_expiration_check',
                'miscellaneous.context_processors.leave_request_check',
                'miscellaneous.context_processors.notice_list_view',
            ],
            'libraries': {
                'custom_tags': 'core.templatetags.template_tags',
            }
        },
    },
]

WSGI_APPLICATION = 'sms.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django_tenants.postgresql_backend',
        'NAME': 'BIDYATek',  
        'USER': 'postgres',  
        'PASSWORD': os.environ.get('DB_PASSWORD', 'P@$$w0rd'),
        'HOST': 'localhost', 
        'PORT': '5432',
    }
}



DATABASE_ROUTERS = (
'django_tenants.routers.TenantSyncRouter',
)

TENANT_MODEL = "organizer.Tenant"  
TENANT_DOMAIN_MODEL = "organizer.Domain"  
# PUBLIC_SCHEMA_URLCONF = ""
SHOW_PUBLIC_IF_NO_TENANT_FOUND =True

# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = '/static/'
# STATIC_URL = 'https://logicunite.com/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR/'media'
MULTITENANT_RELATIVE_MEDIA_ROOT = "tenants/%s"

STORAGES = {
    "default": {
        #"BACKEND": "sms.storage.CustomSchemaStorage",
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
       
    },
}

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AUTH_USER_MODEL = 'shared.CustomUser'

SITE_URL = "http://fulkuri.localhost:8000" 

# DATA_UPLOAD_MAX_NUMBER_FIELDS = 10000



import os

log_file_path = '/home/BIDYATek/FSv01/debug.log'
os.makedirs(os.path.dirname(log_file_path), exist_ok=True)
open(log_file_path, 'w').close() 


CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Asia/Dhaka'


MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'
REPORT_ROOT = os.path.join(MEDIA_ROOT, 'reports')
os.makedirs(REPORT_ROOT, exist_ok=True)

TIME_ZONE = 'Asia/Dhaka'
USE_TZ = True