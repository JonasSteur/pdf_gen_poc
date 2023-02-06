from dataclasses import dataclass, field
from enum import Enum


class FieldErrorCode(Enum):
    INVALID_VALUE = 'invalid_value'
    REQUIRED = 'required'
    TOO_LONG = 'too_long'
    TOO_SHORT = 'too_short'


@dataclass(frozen=True)
class FieldErrorDetails:
    code: FieldErrorCode
    message: str = ''


@dataclass(frozen=True)
class FieldError:
    field: str
    error_details: list[FieldErrorDetails]


class BadRequestErrorCode(Enum):
    INVALID_FIELDS = 'invalid_fields'
    INVALID_QUERY_PARAMETER = 'invalid_query_parameter'
    INVALID_TOKEN = 'invalid_token'
    MISSING_QUERY_PARAMETERS = 'missing_query_parameters'
    UNKNOWN_ERROR = 'unknown_error'


@dataclass(frozen=True)
class BadRequestResponse:
    code: list[BadRequestErrorCode]
    message: str
    incorrect_fields: list[FieldError] = field(default_factory=lambda: [])
