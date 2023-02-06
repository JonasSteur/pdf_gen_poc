from pdf_gen_poc.settings import *  # noqa

# for unit tests we do not want to use redis cache
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}
# We want to run celery tasks immediately, in the same thread
CELERY_TASK_ALWAYS_EAGER = True
# Propagate exceptions, otherwise they would be silently ignored
CELERY_TASK_EAGER_PROPAGATES = True
