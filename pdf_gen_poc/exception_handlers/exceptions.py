from rest_framework.exceptions import APIException
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_500_INTERNAL_SERVER_ERROR,
    HTTP_502_BAD_GATEWAY,
    HTTP_503_SERVICE_UNAVAILABLE,
    HTTP_504_GATEWAY_TIMEOUT,
)

from .objects import BadRequestErrorCode, BadRequestResponse, FieldError, FieldErrorCode, FieldErrorDetails


class BadRequestException(Exception):
    """Use to mark 400 Exception, used as base class for other bad request exceptions"""

    def __init__(self, bad_request_response: BadRequestResponse, status: int = HTTP_400_BAD_REQUEST) -> None:
        self.bad_request_response = bad_request_response
        self.status = status


class FieldMissing(BadRequestException):
    def __init__(self, field: str, message: str = '') -> None:
        bad_request_response = BadRequestResponse(
            code=[BadRequestErrorCode.INVALID_FIELDS],
            message=message,
            incorrect_fields=[FieldError(field=field, error_details=[FieldErrorDetails(code=FieldErrorCode.REQUIRED)])],
        )
        super().__init__(bad_request_response)


class InvalidParameter(BadRequestException):
    def __init__(
        self, field: str, message: str, field_error_code: FieldErrorCode = FieldErrorCode.INVALID_VALUE
    ) -> None:
        bad_request_response = BadRequestResponse(
            code=[BadRequestErrorCode.INVALID_FIELDS],
            message='Invalid parameter',
            incorrect_fields=[
                FieldError(field=field, error_details=[FieldErrorDetails(code=field_error_code, message=message)])
            ],
        )
        super().__init__(bad_request_response)


class InvalidQueryParameter(BadRequestException):
    def __init__(self, field: str, message: str) -> None:
        bad_request_response = BadRequestResponse(
            code=[BadRequestErrorCode.INVALID_QUERY_PARAMETER],
            message='Invalid query parameter',
            incorrect_fields=[
                FieldError(
                    field=field, error_details=[FieldErrorDetails(code=FieldErrorCode.INVALID_VALUE, message=message)]
                )
            ],
        )
        super().__init__(bad_request_response)


class MissingQueryParameters(BadRequestException):
    def __init__(self, parameters: list[str]) -> None:
        incorrect_fields: list[FieldError] = []
        for parameter in parameters:
            incorrect_fields.append(
                FieldError(
                    field=parameter,
                    error_details=[FieldErrorDetails(code=FieldErrorCode.REQUIRED, message='Missing query parameter')],
                )
            )

        bad_request_response = BadRequestResponse(
            code=[BadRequestErrorCode.MISSING_QUERY_PARAMETERS],
            message='Missing query parameters',
            incorrect_fields=incorrect_fields,
        )
        super().__init__(bad_request_response)


class InvalidToken(BadRequestException):
    def __init__(self) -> None:
        bad_request_response = BadRequestResponse(code=[BadRequestErrorCode.INVALID_TOKEN], message='Invalid token')
        super().__init__(bad_request_response)


class UnknownError(Exception):
    def __init__(self, error: str = '') -> None:
        self.status = HTTP_502_BAD_GATEWAY
        self.bad_request_response = BadRequestResponse(
            code=[BadRequestErrorCode.UNKNOWN_ERROR],
            message=f'This action can not be done because of unknown issue: "{error}"',
        )


class ExternalServiceUnavailable(APIException):
    status_code = HTTP_503_SERVICE_UNAVAILABLE
    default_detail = 'Service temporarily unavailable, try again later.'
    default_code = 'service_unavailable'


class ExternalServiceReturnedInvalidData(APIException):
    status_code = HTTP_502_BAD_GATEWAY
    default_detail = 'The server received an invalid response from an upstream server.'
    default_code = 'bad_gateway'

    def __init__(self, message: str = '') -> None:
        self.default_detail = f'{self.default_detail}: {message}' if message else self.default_detail
        super().__init__()


class ExternalServiceTimedOut(APIException):
    status_code = HTTP_504_GATEWAY_TIMEOUT
    default_detail = 'Not receiving a response from the backend servers within the allowed time period.'
    default_code = 'time_out'


class UnreachableCode(Exception):
    status_code = HTTP_500_INTERNAL_SERVER_ERROR
