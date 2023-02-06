from contextlib import ContextDecorator
from logging import getLogger
from typing import Optional, Union

from pybreaker import CircuitBreakerError
from requests import RequestException
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.status import HTTP_503_SERVICE_UNAVAILABLE
from rest_framework.views import exception_handler

from .exceptions import BadRequestException, ExternalServiceUnavailable, UnknownError, UnreachableCode
from .objects import BadRequestErrorCode, BadRequestResponse, FieldError, FieldErrorCode, FieldErrorDetails
from .serializers import BadRequestResponseSerializer

logger = getLogger(__name__)


REST_FIELD_ERRORS_TO_FIELD_ERROR_MAPPING = {
    'This field is required.': FieldErrorCode.REQUIRED,
    'This field may not be blank.': FieldErrorCode.REQUIRED,
}

REST_FIELD_ERROR_PREFIXS_TO_FIELD_ERROR_MAPPING = {
    'Ensure this field has no more than': FieldErrorCode.TOO_LONG,
    'Ensure this field has at least': FieldErrorCode.TOO_SHORT,
}


def _parse_validation_error(errors: list) -> list[FieldErrorDetails]:
    """convert each error to known FieldErrorCode"""
    parsed_errors: list[FieldErrorDetails] = []
    for error in errors:
        code = REST_FIELD_ERRORS_TO_FIELD_ERROR_MAPPING.get(error)
        if code is None:
            [code] = [v for k, v in REST_FIELD_ERROR_PREFIXS_TO_FIELD_ERROR_MAPPING.items() if error.startswith(k)] or [
                FieldErrorCode.INVALID_VALUE
            ]
        parsed_errors.append(FieldErrorDetails(code=code, message=error))
    return parsed_errors


def _parse_field_of_validation_error(field: str, errors: Union[list, dict]) -> list[FieldError]:
    result: list[FieldError] = []
    if isinstance(errors, dict):
        for subfield in errors:
            result += _parse_field_of_validation_error(field=subfield, errors=errors[subfield])
        return result
    if isinstance(errors, list) and len(errors) > 0 and (isinstance(errors[0], dict) or isinstance(errors[0], list)):
        counter = 0
        for error in errors:
            if isinstance(error, dict):
                for subfield in error:
                    result += _parse_field_of_validation_error(
                        field=f'{field}[{counter}].{subfield}', errors=error[subfield]
                    )
            else:
                parsed_error = _parse_validation_error(error)
                result += [FieldError(field=field, error_details=parsed_error)]
            counter += 1
        return result
    parsed_errors = _parse_validation_error(errors)
    return [FieldError(field=field, error_details=parsed_errors)]


def rest_framework_validation_error_handler(error: ValidationError) -> Response:
    incorrect_fields: list[FieldError] = []
    details: list[dict] = [error.detail] if isinstance(error.detail, dict) else error.detail
    for detail in details:
        if isinstance(detail, dict):
            for field in detail:
                incorrect_fields += _parse_field_of_validation_error(field=field, errors=detail[field])
        else:
            incorrect_fields += _parse_field_of_validation_error(field='non_field_errors', errors=[detail])
    bad_request_response = BadRequestResponse(
        code=[BadRequestErrorCode.INVALID_FIELDS], message='Invalid fields', incorrect_fields=incorrect_fields
    )
    data = BadRequestResponseSerializer(instance=bad_request_response).data
    return Response(data, status=400)


def generate_error_response(
    code: list[BadRequestErrorCode],
    message: str,
    status_code: int = 400,
    incorrect_fields: Optional[list[FieldError]] = None,
) -> Response:
    if incorrect_fields is None:
        incorrect_fields = []
    bad_request_response = BadRequestResponse(code, message, incorrect_fields)
    data = BadRequestResponseSerializer(instance=bad_request_response).data
    return Response(data, status=status_code)


class ErrorMapper(ContextDecorator):
    def __init__(self, mapping: dict[type[Exception], Exception]) -> None:
        self.mapping = mapping

    def __enter__(self) -> ContextDecorator:
        return self

    def __exit__(self, exception_type: type[Exception], *args) -> bool:
        if exception_type is None:
            return True

        mapped_exception = self.mapping.get(exception_type)
        if mapped_exception:
            raise mapped_exception
        logger.warning('An error (%s) was not mapped. Make a ticket to add it.', exception_type)
        return False


def general_exception_handler(exception: Exception, context: Optional[dict] = None) -> Optional[Response]:
    if isinstance(exception, CircuitBreakerError):
        return Response(status=HTTP_503_SERVICE_UNAVAILABLE, data={'detail': str(exception)})

    if isinstance(exception, RequestException):
        exception = ExternalServiceUnavailable()
    if isinstance(exception, (BadRequestException, UnknownError)):
        data = BadRequestResponseSerializer(instance=exception.bad_request_response).data
        if isinstance(exception, UnknownError):
            logger.exception(data['message'])
            return Response(data, status=exception.status)
        return Response(data, status=exception.status)
    if isinstance(exception, ValidationError):
        return rest_framework_validation_error_handler(exception)
    if isinstance(exception, UnreachableCode):
        logger.error('Code that should be unreachable is touched', exc_info=True)
        return Response(status=500)

    return exception_handler(exception, context)
