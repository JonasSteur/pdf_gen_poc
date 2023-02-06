from logging import WARNING

from environ import Env
from sentry_sdk import init as sentry_sdk_init
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.logging import LoggingIntegration, ignore_logger
from sentry_sdk.integrations.redis import RedisIntegration

env = Env(
    DEBUG=(bool, False),
)

# Config context is production, acc, dev, but can also be dev.[username] etc
CONFIG_CONTEXT = env('DJANGO_CONFIG_CONTEXT', default='dev')


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'root': {
        # Start logging at INFO level, specify stricter levels further in handlers and loggers
        'level': env('LOG_LEVEL', default='INFO'),
        'handlers': ['console'],
    },
    'filters': {
        'request_id': {'()': 'pdf_gen_poc.logging.filters.RequestIDFilter'},
        'celery_task_id': {'()': 'pdf_gen_poc.logging.filters.CeleryTaskIDFilter'},
    },
    'formatters': {
        'verbose': {'format': '%(levelname)s %(asctime)s [%(request_id)s] %(module)s %(message)s'},
        'json': {'()': 'pdf_gen_poc.logging.formatters.JSONFormatter'},
    },
    'handlers': {
        'null': {
            # Eat all log messages with this handler
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },
        'console': {
            # Send everything to the console
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'filters': ['request_id', 'celery_task_id'],
            'formatter': env('LOG_FORMATTER', default='json'),
        },
        'statsd_csrf': {
            'level': 'INFO',
            'class': 'pdf_gen_poc.logging.handlers.StatsdHandler',
            'statsd_key': 'exceptions.django.csrf',
        },
    },
    'loggers': {
        # ignore django warnings about missing or incorrect csrf tokens
        'django.security.csrf': {
            'handlers': ['statsd_csrf'],
            'propagate': False,
        },
        # DisallowedHost errors happen early, we need to catch those separately
        'django.security.DisallowedHost': {
            'handlers': ['null'],
            'propagate': False,
        },
        # Don't log django request warnings (4xx status code)
        'django.request': {
            'level': 'INFO',
            'handlers': ['null'],
            'propagate': False,
        },
        'celery': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': True,
        },
        'django_auth_ldap': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': True,
        },
    },
}

# Sentry logging
KEYS_TO_SCRUB = (
    'password',
    'secret',
    'passwd',
    'authorization',
    'api_key',
    'apikey',
    'sentry_dsn',
    'access_token',
    'refresh_token',
    'client_secret',
)


def scrub_sensitive_data(event, hint):
    """
    Redact away some keys, so they don't show up in the logging. We define this here because importing things in the app
    from the settings file is likely to lead to disaster (as this gets loaded before Django is started).
    """
    event_data = event.get('request', {})
    for k, _ in event_data.get('data', {}).items():
        if k.lower() in KEYS_TO_SCRUB:
            event['request']['data'][k] = '[Filtered]'
    for k, _ in event_data.get('headers', {}).items():
        if k.lower() in KEYS_TO_SCRUB:
            event['request']['headers'][k] = '[Filtered]'
    return event


sentry_sdk_init(
    dsn=env('SENTRY_DSN', default=None),
    integrations=[
        DjangoIntegration(),
        CeleryIntegration(),
        RedisIntegration(),
        LoggingIntegration(event_level=WARNING),
    ],
    before_send=scrub_sensitive_data,
    environment=CONFIG_CONTEXT,
)
ignore_logger('django.security.DisallowedHost')

# Runtime context is uwsgi.www, manage.runserver, manage.celeryd, ...
RUNTIME_CONTEXT = env('DJANGO_RUNTIME_CONTEXT', default='')
if RUNTIME_CONTEXT == '':
    import sys  # noqa

    if env.bool('DJANGO_IS_MANAGEMENT_COMMAND', default=False) and len(sys.argv) > 1:
        RUNTIME_CONTEXT = f'manage.{sys.argv[1]}'
    else:
        # Double __empty__ for consistent Graphite queries
        RUNTIME_CONTEXT = '__empty__.__empty__'

# StatsD configuration
STATSD_HOST = env('STATSD_HOST', default='')
STATSD_PREFIX = '.'.join([CONFIG_CONTEXT, 'pdf_gen_poc', 'stats', RUNTIME_CONTEXT])
STATSD_CLIENT = 'django_statsd.clients.normal' if STATSD_HOST else 'django_statsd.clients.null'
STATSD_PATCHES = ['django_statsd.patches.db', 'django_statsd.patches.cache']
STATSD_MODEL_SIGNALS = True
STATSD_CELERY_SIGNALS = True
STATSD_AUTH_SIGNALS = True
