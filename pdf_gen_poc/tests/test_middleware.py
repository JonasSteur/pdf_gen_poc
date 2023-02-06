from unittest.mock import MagicMock

from django.http import HttpResponse
from django.test import RequestFactory

from ..middleware import EmptyOptionalFieldsMiddleware


class TestEmptyOptionalFieldsMiddleware:
    def test_remove_correct_fields(self, rf: RequestFactory) -> None:
        middleware = EmptyOptionalFieldsMiddleware(get_response=MagicMock())
        request = rf.get('/')
        response: HttpResponse = HttpResponse()
        response.data = {
            'field': 'value',
            'zero': 0,
            'false': False,
            'empty': '',
            'None': 'None',
            'Null': 'null',
            'to_remove': None,
            'nested': {'to_remove': None},
            'list': [{'to_remove': None}],
        }
        middleware.process_response(request, response)
        assert response.data == {
            'field': 'value',
            'zero': 0,
            'false': False,
            'empty': '',
            'None': 'None',
            'Null': 'null',
            'nested': {},
            'list': [{}],
        }

    def test_response_with_no_data(self, rf: RequestFactory) -> None:
        middleware = EmptyOptionalFieldsMiddleware(get_response=MagicMock())
        request = rf.get('/')
        response: HttpResponse = HttpResponse()
        middleware.process_response(request, response)

    def test_response_with_data_none(self, rf: RequestFactory) -> None:
        middleware = EmptyOptionalFieldsMiddleware(get_response=MagicMock())
        request = rf.get('/')
        response: HttpResponse = HttpResponse()
        response.data = None
        middleware.process_response(request, response)
        assert response.content == bytes()

    def test_call(self, rf: RequestFactory) -> None:
        middleware = EmptyOptionalFieldsMiddleware(get_response=lambda x: {})
        request = rf.get('/')
        middleware.__call__(request)
