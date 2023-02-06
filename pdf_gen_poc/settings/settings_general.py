from logging import WARNING
from os import path

from corsheaders.defaults import default_headers
from environ import Env, Path

# Django-environ basics
root = Path(__file__) - 2
env = Env(
    DEBUG=(bool, False),
)

# Read a file with environment variables, these variables can be used to set the value of django settings
ENV_FILE = str(env.path('ENV_FILE', default='.env'))
if path.isfile(ENV_FILE):
    Env.read_env(ENV_FILE)
else:
    # unset if no file was found
    ENV_FILE = None

# Build paths inside the project like this: path.join(BASE_DIR, ...)
BASE_DIR = root()

# Django Debug option
DEBUG = env.bool('DEBUG')

CONFIG_CONTEXT = env('DJANGO_CONFIG_CONTEXT', default='dev')

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY', default='ffewewp078_e($rtuop)!y)845@$@^^f9x3##^**(hm(_c')

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=[])

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # shell plus
    'django_extensions',
    # Django REST framework
    'rest_framework',
    # CORS headers
    'corsheaders',
    # OAuth2
    'oauth2_provider',
    # pdf_gen_poc
    'pdf_gen_poc',
    # waffle
    'waffle',
]

MIDDLEWARE = [
    # Log request timing to statsd. Should be the very first to get the timing correct
    'django_statsd.middleware.GraphiteRequestTimingMiddleware',
    'django_statsd.middleware.GraphiteMiddleware',
    'pdf_gen_poc.logging.middleware.save_request_body',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    # Whitenoise to handle static
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'pdf_gen_poc.logging.middleware.request_id',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'oauth2_provider.middleware.OAuth2TokenMiddleware',
    'waffle.middleware.WaffleMiddleware',
    'pdf_gen_poc.middleware.EmptyOptionalFieldsMiddleware',
    'pdf_gen_poc.logging.middleware.request_log',
]

ROOT_URLCONF = 'pdf_gen_poc.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'pdf_gen_poc.wsgi.application'

# Database
DATABASES = {
    'default': env.db('DATABASE_URL', default='sqlite://:memory:'),
}
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = env('STATIC_ROOT', default=root('static'))
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# All logins happen through the admin
LOGIN_URL = '/admin/login/'

CACHE_URL = env('CACHE_URL', default='redis://localhost:6379/0')

# Caches configurations
CACHES = {
    'default': env.cache('CACHE_URL', default='redis://localhost:6379/0'),
}

# Django REST framework settings
REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': ('rest_framework.renderers.JSONRenderer',),
    'DEFAULT_PERMISSION_CLASSES': ('rest_framework.permissions.IsAuthenticated',),
    'DEFAULT_AUTHENTICATION_CLASSES': ('oauth2_provider.contrib.rest_framework.OAuth2Authentication',),
    'EXCEPTION_HANDLER': 'pdf_gen_poc.exception_handlers.general_exception_handler',
}

# Security options
HAS_SSL = env.bool('HAS_SSL', default=False)
VERIFY_SSL = env.bool('VERIFY_SSL', default=True)

if HAS_SSL:
    SECURE_HSTS_SECONDS = 24 * 365 * 60 * 60  # 1 year

SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_SSL_REDIRECT = env.bool('HAS_SSL', default=False)

CSRF_COOKIE_SECURE = env.bool('HAS_SSL', default=False)
CSRF_COOKIE_HTTPONLY = True

# waffle settings
WAFFLE_LOG_MISSING_FLAGS = WARNING
WAFFLE_LOG_MISSING_SWITCHES = WARNING
WAFFLE_LOG_MISSING_SAMPLES = WARNING

# CORS headers settings
CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_HEADERS = list(default_headers) + ['X-Request-Id']  # Used for correlating requests with each other
CORS_EXPOSE_HEADERS = (
    'WWW-Authenticate',  # Mandatory in a 401 - used by client to determine whether sending a refresh token is needed
    'X-Request-Id',  # Used for correlating requests with each other
)
CORS_ALLOW_CREDENTIALS = True
