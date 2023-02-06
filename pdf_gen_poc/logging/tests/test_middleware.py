from logging import Logger
from unittest.mock import Mock

from django.http import HttpRequest, HttpResponse
from rest_framework.test import APIRequestFactory
from waffle.testutils import override_switch

from ..middleware import LOG_ACCESS_TOKEN, LOG_BAD_REQUEST_RESPONSE, LOG_BODY, request_id, request_log


def _get_response(request: HttpRequest) -> HttpResponse:
    return HttpResponse()


def test_passes_auth_header() -> None:
    logger = Mock(spec=Logger)
    request = APIRequestFactory().get('/')
    request.META['HTTP_AUTHORIZATION'] = 'Bearer abcdefghijklmopqrstuvwxyz'
    with override_switch(LOG_ACCESS_TOKEN, True):
        request_log(_get_response, logger)(request)
    _, kwargs = logger.info.call_args
    assert kwargs['extra']['token'] == 'abcdefgh'


def test_does_not_passes_auth_header_or_body() -> None:
    logger = Mock(spec=Logger)
    request = APIRequestFactory().get('/')
    request.META['HTTP_AUTHORIZATION'] = 'test'
    with override_switch(LOG_ACCESS_TOKEN, False), override_switch(LOG_BODY, False):
        request_log(_get_response, logger)(request)

    _, kwargs = logger.info.call_args
    assert not kwargs['extra'].get('token')
    assert not kwargs['extra'].get('body')


def test_passes_json_body() -> None:
    logger = Mock(spec=Logger)
    request = APIRequestFactory().post('/', data='{"key": "value"}', content_type='application/json')
    with override_switch(LOG_BODY, True):
        request_log(lambda request: HttpResponse(status=400), logger)(request)
    _, kwargs = logger.info.call_args
    assert kwargs['extra']['body'] == {'key': 'value'}


def test_passes_json_body_get_request() -> None:
    logger = Mock(spec=Logger)
    request = APIRequestFactory().get('/', content_type='application/json')
    with override_switch(LOG_BODY, True):
        request_log(lambda request: HttpResponse(status=400), logger)(request)
    _, kwargs = logger.info.call_args
    assert not kwargs['extra'].get('body')


def test_passes_json_invalid_body() -> None:
    logger = Mock(spec=Logger)
    request = APIRequestFactory().post('/', data='', content_type='application/json')
    with override_switch(LOG_BODY, True):
        request_log(lambda request: HttpResponse(status=400), logger)(request)
    _, kwargs = logger.info.call_args
    assert not kwargs['extra'].get('body')


def test_passes_body_form_encoded() -> None:
    logger = Mock(spec=Logger)
    request = APIRequestFactory().post(
        '/', data='key=value&key2=value2}', content_type='application/x-www-form-urlencoded'
    )
    with override_switch(LOG_BODY, True):
        request_log(lambda request: HttpResponse(status=400), logger)(request)
    _, kwargs = logger.info.call_args
    assert kwargs['extra'].get('body') is None


def test_do_not_body_form_encoded_oauth() -> None:
    logger = Mock(spec=Logger)
    request = APIRequestFactory().post(
        '/jim/oauth2/token/', data='key=value&key2=value2}', content_type='application/x-www-form-urlencoded'
    )
    with override_switch(LOG_BODY, True):
        request_log(lambda request: HttpResponse(status=400), logger)(request)
    _, kwargs = logger.info.call_args
    assert kwargs['extra']['body'] == {'oauth2 request'}


def test_passes_sanitized_json_body() -> None:
    logger = Mock(spec=Logger)
    request = APIRequestFactory().post('/', data='{"password": "secret"}', content_type='application/json')
    with override_switch(LOG_BODY, True):
        request_log(lambda request: HttpResponse(status=400), logger)(request)
    _, kwargs = logger.info.call_args
    assert kwargs['extra']['body'] == {'password': '***'}


def test_log_bad_request_response() -> None:
    logger = Mock(spec=Logger)
    request = APIRequestFactory().post('/', data='{"key": "value"}', content_type='application/json')
    with override_switch(LOG_BAD_REQUEST_RESPONSE, True):
        request_log(lambda request: HttpResponse(status=400, content='bad response'), logger)(request)
    _, kwargs = logger.info.call_args
    assert kwargs['extra']['response'] == b'bad response'


def test_request_id_with_header() -> None:
    request = APIRequestFactory().post(
        '/jim/oauth2/token/',
        data='key=value&key2=value2}',
        content_type='application/x-www-form-urlencoded',
        HTTP_X_REQUEST_ID='test',
    )
    response = request_id(lambda request: HttpResponse(status=400))(request)
    assert response.get('X-Request-Id') == 'test'


def test_request_id_without_header() -> None:
    request = APIRequestFactory().post(
        '/jim/oauth2/token/', data='key=value&key2=value2}', content_type='application/x-www-form-urlencoded'
    )
    response = request_id(lambda request: HttpResponse(status=400))(request)
    assert not response.has_header('X-Request-Id')
