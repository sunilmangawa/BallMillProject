import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-og$0ubxfp77p!+f0e*&nv10ecu75i+ao7s#dkukpznj-$uw=nk'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['*']#194.31.53.193-ballmilautomation.com-www.ballmilautomation.com"'

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # New Apps
    'accounts.apps.AccountsConfig', # new
    'pages.apps.PagesConfig', # new
    'blog.apps.BlogConfig', # new
    'milldata.apps.MilldataConfig',


    # Third party apps
    'rest_framework',
    'crispy_forms', # new
    'crispy_bootstrap5', # new

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

ROOT_URLCONF = 'ballmillautomation.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates"], # new
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


WSGI_APPLICATION = 'ballmillautomation.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases
'''
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
'''
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'OPTIONS': {
            'read_default_file': '/etc/mysql/my.cnf',
        },
    }
}

# [client]
# database = ballmillautoDB
# user = coder
# password = str(#Brahma4coder)
# default-character-set = utf8
# END

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'ballmillautoDB',
        'USER': 'coder',
        'PASSWORD': '#Brahma4coder',
        'HOST': 'localhost',
        'PORT': '',
        'OPTIONS': {
            'charset': 'utf8mb4', 
            'init_command': "SET time_zone='+05:30';",
        },
    }
}


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


LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Kolkata'#'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

#STATIC_URL = '/static/'
STATIC_URL = '/python/static/'
#STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static'),]
#STATICFILES_DIRS = [BASE_DIR / 'static']
# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

#STATIC_ROOT = os.path.join(BASE_DIR, 'static') #gpt
STATIC_ROOT = '/usr/local/lsws/Example/html/webapp/static'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = "accounts.CustomUser" # new

# LOGIN_URL = "login"
# LOGIN_REDIRECT_URL = "home" # new
LOGOUT_REDIRECT_URL = "home" # new

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5" # new
CRISPY_TEMPLATE_PACK = "bootstrap5" # new

# EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend" # new
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

EMAIL_HOST = 'smtp.gmail.com'  # e.g., 'smtp.gmail.com' for Gmail
EMAIL_PORT = 587  # e.g., 587 for Gmail
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'ballmillautomation@gmail.com'
EMAIL_HOST_PASSWORD = 'Test4work'
DEFAULT_FROM_EMAIL = 'ballmillautomation@gmail.com'


