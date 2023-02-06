from collections.abc import Callable
from json import dumps
from typing import Any

from django.http import HttpRequest, HttpResponse
from rest_framework.utils.encoders import JSONEncoder


class EmptyOptionalFieldsMiddleware(object):
    """
    Delete empty fields in response dicts.
    Example:
        data = {
            'foo': 'None,
            'bar': [{'baz': None, 'qux': 'quux'}, {'corge': 'uier'}]
            'grault': {'garply': None, 'waldo': 'fred'}
        }
    If this example is returned this middleware will filter out the fields data['foo'], data['bar'][0]['baz'] and
    data['grault']['graply']
    """

    def __init__(self, get_response: Callable) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> Any:
        response = self.get_response(request)
        return self.process_response(request, response)

    def process_response(self, request: HttpRequest, response: HttpResponse):
        if hasattr(response, 'data'):
            # converting `None` to json is `'null'` we don't want that
            if response.data is None:
                return response
            self._remove_none_fields(response.data)
            response.content = dumps(response.data, cls=JSONEncoder).encode()
        return response

    def _remove_none_fields(self, data):
        if isinstance(data, dict):
            self._remove_none_fields_from_dict(data)
        elif isinstance(data, list):
            for i in data:
                self._remove_none_fields(i)

    def _remove_none_fields_from_dict(self, data):
        keys_to_remove = []
        for key, value in data.items():
            if value is None:
                keys_to_remove.append(key)
            else:
                self._remove_none_fields(value)
        for key in keys_to_remove:
            data.pop(key)
