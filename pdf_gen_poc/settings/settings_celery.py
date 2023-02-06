from environ import Env
from requests.exceptions import RequestException

env = Env(
    DEBUG=(bool, False),
)

# Celery (task queue) settings
# Do mind every celery setting must have the prefix CELERY_
CELERY_BROKER_URL = env('CELERY_BROKER_URL', default='redis://0.0.0.0:6379/0')  # Where Celery's task log is stored
CELERY_TASK_ALWAYS_EAGER = env.bool('CELERY_TASK_ALWAYS_EAGER', False)
CELERY_BROKER_TRANSPORT_OPTIONS = env(
    'CELERY_BROKER_TRANSPORT_OPTIONS',
    default={'visibility_timeout': 1800},
    cast={'value': str, 'cast': {'visibility_timeout': int}},
)
CELERY_BROKER_CONNECTION_MAX_RETRIES = 5

CELERY_DEFAULT_QUEUE = 'default'
CELERY_DEFAULT_EXCHANGE = 'default'
CELERY_DEFAULT_ROUTING_KEY = 'default'
CELERY_SEND_TASK_ERROR_EMAILS = False
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TRACK_STARTED = True

CELERY_TIMEZONE = 'UTC'
CELERY_BEAT_SCHEDULE = {}
CELERY_ANNOTATIONS = {'*': {'throws': (RequestException,)}}
