from os import environ

from celery import Celery, signals

# set the default Django settings module for the 'celery' program.
environ.setdefault('DJANGO_SETTINGS_MODULE', 'pdf_gen_poc.settings')

app = Celery('pdf_gen_poc')

# Using a string here means the worker don't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

# We need to stop Celery from overriding our logging, or things won't reach Sentry
@signals.setup_logging.connect
def setup_logging(**kwargs):
    pass
