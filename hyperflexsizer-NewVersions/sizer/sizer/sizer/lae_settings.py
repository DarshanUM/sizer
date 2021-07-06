"""
Django settings for sizer project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.realpath(__file__))
BASE_DIR = os.path.join(BASE_DIR, '..')
OVA_BASE_DIR = os.path.join(BASE_DIR, '../../ova-download')

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '-+5@a^)0tmxgt@f496b4r2rc#=_u0mo(m&j-om4d_cju4p#s)%'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'djoser',
    'hyperconverged',
    'rest_framework',
    'rest_framework.authtoken',
    'rest_framework_swagger',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'middleware.exception.ExceptionMiddleware',
    'middleware.sizer_access.SizerAccess',
    'middleware.crossdomainxhr.XsSharing'
)
XS_SHARING_ALLOWED_ORIGINS = ['http://127.0.0.1:8000','http://127.0.0.1:9010','http://localhost:9010']
XS_SHARING_ALLOWED_METHODS = ['POST','GET','OPTIONS', 'PUT', 'DELETE']
XS_SHARING_ALLOWED_HEADERS = ['Content-Type', '*', 'Authorization', 'X-CSRFToken']

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
    ),
}

DJOSER = {
   # 'DOMAIN': 'frontend.com',
   # 'SITE_NAME': 'Frontend',
    'PASSWORD_RESET_CONFIRM_URL': '#/password/reset/confirm/{uid}/{token}',
    'ACTIVATION_URL': '#/activate/{uid}/{token}',
    'LOGIN_AFTER_ACTIVATION': False,
    'SEND_ACTIVATION_EMAIL': False,
}

ROOT_URLCONF = 'urls'

WSGI_APPLICATION = 'sizer.wsgi.application'

# set database parameters
# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

from urlparse import urlparse
db_url = urlparse(os.environ.get('OPENSHIFT_MYSQL_DB_URL'))


DATABASES = {
    'default': {
        'ENGINE':'django.db.backends.mysql',
        'NAME': os.environ['OPENSHIFT_APP_NAME'],
        'USER':db_url.username,
        'PASSWORD':db_url.password,
        'HOST': db_url.hostname,
        'PORT': db_url.port,
            }
        }




# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, '..', 'static')

# UI code
UI_ROOT = os.path.join(BASE_DIR, 'webapps/dist/')
UI_URL = 'ui/'

import time
filename = os.path.join(BASE_DIR,'logs', time.strftime('%d-%m-%Y')+'.log')
FILE_SIZE_MB = 5

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format' : "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt' : "%d/%b/%Y %H:%M:%S"
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': filename,
            'maxBytes' : 1000000*FILE_SIZE_MB,
            'backupCount' : 5,
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'django': {
            'handlers':['file'],
            'propagate': True,
            'level':'ERROR',
        },
        'hyperconverged': {
            'handlers': ['file'],
            'level': 'DEBUG',
	},
        'middleware': {
            'handlers': ['file'],
            'level': 'DEBUG',
        }
    }
}

import datetime

TOKEN_LIFE_SPAN = datetime.timedelta(hours = 24)

# Swagger settings

SWAGGER_SETTINGS = {
    'exclude_namespaces': [],
    'api_version': '0.1',
    'api_path': '/',
    'enabled_methods': [
        'get',
        'post',
        'put',
        'patch',
        'delete'
    ],
    'api_key': '',
    'is_authenticated': False,
    'is_superuser': False,
    'permission_denied_handler': None,
    'resource_access_handler': None,
    'base_path': "10.11.0.173" + ':' + "9090" + '/docs',
    'info': {
        'contact': '',
        'description': '',
        'license': 'Apache 2.0',
        'licenseUrl': 'http://www.apache.org/licenses/LICENSE-2.0.html',
        'termsOfServiceUrl': '',
        'title': 'Sizer  REST API documentation',
    },
    'doc_expansion': 'none',
}


LDAP_URL = 'ldap://dsx.cisco.com:389'
LDAP_BIND_DETAILS = 'uid=hxsizerad.gen,OU=Generics,O=cco.cisco.com'
LDAP_PASSWORD = 'Agile@123'

LAE_FROM = "donotreply@cisco.com"
LAE_TO = "hx-sizer@external.cisco.com"
LAE_HOST = "outbound.cisco.com"

STAGE_FROM = "maple-noreply@maplelabs.com"
STAGE_TO = "saleem.sheikh@maplelabs.com"
STAGE_HOST = "webmail.xoriant.com"

local_stage_url = "http://10.11.0.150:8000/ui/index.html#/scenario"
lae_stage_url = "https://hyperflexsizer-stage.cloudapps.cisco.com/ui/index.html#/scenario"
lae_prod_url = "https://hyperflexsizer.cloudapps.cisco.com"
