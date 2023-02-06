from uuid import uuid4

from celery import Task, current_task

from .logging import local_thread


def get_request_id_or_task_id() -> str:
    return (
        current_task.request.id.split(':')[-1]
        if current_task and current_task.request.id
        else getattr(local_thread, 'request_id', '')
    )


class TraceableTask(Task):
    def _generate_task_id(self) -> str:
        task_id = str(uuid4())
        request_id = getattr(local_thread, 'request_id', None)
        parent_task_id = current_task.request.id[:-28] if current_task and hasattr(current_task, 'request') else None
        task_id = f'{parent_task_id or request_id}:{task_id}' if parent_task_id or request_id else task_id
        return task_id

    def apply_async(self, args=None, kwargs=None, task_id=None, **options):
        task_id = task_id or self._generate_task_id()
        return super().apply_async(args=args, kwargs=kwargs, task_id=task_id, **options)
