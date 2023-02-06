from unittest.mock import patch

from celery import shared_task
from pytest import mark

from ..logging import local_thread
from ..utils import TraceableTask, get_request_id_or_task_id


class TestGetRequestIdOrTaskId:
    def test_get_request_id_or_task_id(self):
        assert get_request_id_or_task_id() == ''


class TestTraceableTask:
    @mark.parametrize(
        'request_id,parent_id,task_id,expected',
        [
            ('request-id', 'parentid-of-length-36-like-a-guuid-4', 'taskid', 'parentid:taskid'),
            ('', 'request-id:parentid-of-length-36-like-a-guuid-4', 'taskid', 'request-id:parentid:taskid'),
            ('request-id', '', 'taskid', 'request-id:taskid'),
            ('', '', 'taskid', 'taskid'),
        ],
    )
    def test_apply_async_with_generated_task_id(self, request_id: str, parent_id: str, task_id: str, expected: str):
        @shared_task(base=TraceableTask)
        def dummy() -> None:
            return None

        assert dummy() is None  # coverage

        local_thread.request_id = request_id
        with patch('pdf_gen_poc.utils.uuid4', return_value=task_id), patch(
        'celery.app.task.Task.apply') as apply, patch(
            'pdf_gen_poc.utils.current_task'
        ) as mock_current_task:
            mock_current_task.request.id = parent_id
            dummy.delay()

        apply.assert_called()
        assert apply.call_args.kwargs['task_id'] == expected
