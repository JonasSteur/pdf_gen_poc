from ..objects import BadRequestErrorCode, BadRequestResponse, FieldError, FieldErrorCode, FieldErrorDetails
from ..serializers import BadRequestResponseSerializer


def test_bad_request_response_serializer() -> None:
    bad_request_response = BadRequestResponse(
        code=[BadRequestErrorCode.INVALID_FIELDS],
        message='oeps',
        incorrect_fields=[
            FieldError(
                field='test',
                error_details=[
                    FieldErrorDetails(code=FieldErrorCode.INVALID_VALUE),
                    FieldErrorDetails(code=FieldErrorCode.TOO_SHORT, message='Way too short!'),
                ],
            )
        ],
    )
    data = BadRequestResponseSerializer(instance=bad_request_response).data
    assert data == {
        'code': [BadRequestErrorCode.INVALID_FIELDS.value],
        'message': 'oeps',
        'incorrect_fields': [
            {
                'field': 'test',
                'errors': [
                    {'code': FieldErrorCode.INVALID_VALUE.value, 'message': ''},
                    {'code': FieldErrorCode.TOO_SHORT.value, 'message': 'Way too short!'},
                ],
            }
        ],
    }
