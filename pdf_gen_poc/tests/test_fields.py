from pytest import raises
from rest_framework.exceptions import ValidationError

from ..exception_handlers.fields import BadRequestErrorCodeField
from ..exception_handlers.objects import BadRequestErrorCode
from ..fields import EnumField, MultipleEnumField


class TestEnumField:
    def test_to_internal_value(self) -> None:
        with raises(ValidationError):
            EnumField().to_internal_value('test')

    def test_to_internal_value_required(self) -> None:
        with raises(ValidationError):
            EnumField(required=True).to_internal_value('')

    def test_to_internal_value_not_found(self) -> None:
        with raises(ValidationError):
            EnumField().to_internal_value('test')


class TestMultipleEnumField:
    def test_to_internal_value(self) -> None:
        assert BadRequestErrorCodeField().to_internal_value([BadRequestErrorCode.INVALID_FIELDS.value]) == [
            BadRequestErrorCode.INVALID_FIELDS
        ]

    def test_raises_error_if_required_and_not_given(self) -> None:
        with raises(ValidationError):
            MultipleEnumField(required=True).to_internal_value([])

    def test_raises_error_if_unknown_value(self) -> None:
        with raises(ValidationError):
            MultipleEnumField(required=False).to_internal_value(['test'])
