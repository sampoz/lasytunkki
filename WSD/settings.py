"""
Django settings for WSD project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))



# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'ugzze3xnc2d^2a#+&72ic=j)@&)_y*wq#p@e8_n$1(3$&z(i54'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False
TEMPLATE_DEBUG = False

ALLOWED_HOSTS = [
    '.herokuapp.com',
    'smtp.google.com',
]

SITE_ID=1

# Application definition

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.admin',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django.templatetags',

    # App
    'Laulutunkki',

    # Search
    'whoosh',
    'haystack',

    # Comments
    'django.contrib.sites',
    'crispy_forms',
    'fluent_comments',
    'django.contrib.comments',  # Needs to be below fluent_comments and the app

    # South
    'south',

    # Third party login allaccess
    'allaccess',
)

SESSION_ENGINE = 'django.contrib.sessions.backends.db'

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'WSD.urls'

TEMPLATE_DIRS = (os.path.join(BASE_DIR, 'templates/'))
FIXTURE_DIRS = (os.path.join(BASE_DIR, 'fixtures/'))

WSGI_APPLICATION = 'WSD.wsgi.application'

# OpenID stuff
AUTHENTICATION_BACKENDS = (
    # Default backend
    'django.contrib.auth.backends.ModelBackend',
    # Additional backend
    'allaccess.backends.AuthorizedServiceBackend',
)

LOGIN_URL = '/'
LOGIN_REDIRECT_URL = '/'

# For Profiles
AUTH_PROFILE_MODULE = 'Laulutunkki.UserProfile'
SESSION_SERIALIZER = 'django.contrib.sessions.serializers.PickleSerializer'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}
# For HEROKU:
# Parse database configuration from $DATABASE_URL
if os.environ.get('DATABASE_URL', None):
    import dj_database_url
    DATABASES['default'] = dj_database_url.config()

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'fi-FI'
TIME_ZONE = 'Europe/Helsinki'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'
#STATICFILES_DIRS = (
    #os.path.join(BASE_DIR, "static"),
#)
STATIC_ROOT = os.path.join(BASE_DIR, "static")

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, "media")


# Search (whoosh and haystack)

#Kopioi enne herokuun laittoo etta seuraava enabloidaan
# ja jalkimmainen disabloidaan

# Haystack
HAYSTACK_CONNECTIONS = {
    'default' : {
        'ENGINE' : 'haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine',
        'URL' : os.environ['SEARCHBOX_URL'],
        'INDEX_NAME': 'lasytunkki',
    },
}

'''
# Whoosh
WHOOSH_INDEX = os.path.join(BASE_DIR, "whoosh_index")

# Haystack
HAYSTACK_CONNECTIONS = {
    'default' : {
        'ENGINE' : 'haystack.backends.whoosh_backend.WhooshEngine',
        'PATH' : WHOOSH_INDEX,
    },
}
'''

HAYSTACK_SIGNAL_PROCESSOR = 'haystack.signals.RealtimeSignalProcessor'

# Cripsy forms
CRISPY_TEMPLATE_PACK = 'bootstrap3'

# Comments (fluent-comments)
FLUENT_COMMENTS_EXCLUDE_FIELDS = ('name', 'email', 'url')
COMMENTS_APP = 'fluent_comments'


# Gmail mail server settings and logins for account management

EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = 'laulutunkki@gmail.com'
SERVER_EMAIL = 'laulutunkki@gmail.com'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'laulutunkki@gmail.com'
EMAIL_HOST_PASSWORD = 'tik-laulutunkki'
    
    
