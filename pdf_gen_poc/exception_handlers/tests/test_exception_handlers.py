from unittest.mock import patch

from django.http import Http404
from pybreaker import CircuitBreakerError
from pytest import mark
from requests.exceptions import Timeout
from rest_framework.exceptions import ErrorDetail, ValidationError

from .. import general_exception_handler, generate_error_response
from ..exceptions import UnknownError, UnreachableCode
from ..objects import BadRequestErrorCode, FieldError, FieldErrorCode, FieldErrorDetails


def test_generate_error_response() -> None:
    response = generate_error_response(
        code=[BadRequestErrorCode.INVALID_FIELDS],
        message='Test message',
        status_code=401,
        incorrect_fields=[FieldError('field', [FieldErrorDetails(code=FieldErrorCode.INVALID_VALUE)])],
    )
    assert response.status_code == 401
    assert response.data['code'] == ['invalid_fields']
    assert response.data['message'] == 'Test message'
    field_error = response.data['incorrect_fields'][0]
    assert field_error['field'] == 'field'
    assert field_error['errors'][0]['code'] == 'invalid_value'


def test_generate_error_response_default_values() -> None:
    response = generate_error_response(code=[BadRequestErrorCode.INVALID_FIELDS], message='Test message')
    assert response.status_code == 400
    assert response.data['code'] == ['invalid_fields']
    assert response.data['message'] == 'Test message'
    assert response.data['incorrect_fields'] == []


def test_general_exception_handler_standard_404() -> None:
    exception = Http404()
    response = general_exception_handler(exception)
    assert response
    assert response.status_code == 404


@mark.parametrize(
    'exception, expected_status',
    [
        (UnknownError(error='oeps'), 502),
        (Timeout(), 503),
        (ValidationError('test'), 400),
        (UnreachableCode(), 500),
    ],
)
def test_errors(exception: Exception, expected_status: int) -> None:
    response = general_exception_handler(exception)
    assert response
    assert response.status_code == expected_status
    assert isinstance(response.data, dict) or response.data is None


def test_logged_exception_for_unknown_error() -> None:
    with patch('pdf_gen_poc.exception_handlers.logger') as logger_mock:
        general_exception_handler(UnknownError())
    assert logger_mock.method_calls


def test_general_exception_handler_nested_errors_in_list() -> None:
    exception = ValidationError({'field': [{}, [ErrorDetail(string='Invalid field', code='invalid')]]})
    response = general_exception_handler(exception)
    assert response
    assert response.status_code == 400


def test_general_exception_handler_external_request_exception() -> None:
    response = general_exception_handler(Timeout())
    assert response
    assert response.status_code == 503


def test_general_exception_handler_circuit_breaker_error() -> None:
    response = general_exception_handler(CircuitBreakerError())
    assert response
    assert response.status_code == 503
