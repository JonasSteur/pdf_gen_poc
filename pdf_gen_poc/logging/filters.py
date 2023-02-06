from logging import Filter

from celery import current_task

from . import local_thread


class RequestIDFilter(Filter):
    def filter(self, record):
        record.request_id = getattr(local_thread, 'request_id', None)
        return True


class CeleryTaskIDFilter(Filter):
    def filter(self, record):
        record.celery_task_id = current_task.request.id if current_task and hasattr(current_task, 'request') else None
        return True
