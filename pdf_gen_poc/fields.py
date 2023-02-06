from enum import Enum

from rest_framework import serializers
from rest_framework.exceptions import ValidationError


class EnumField(serializers.Field):
    """Base class to serialize enum fields. Override `default_value` and `MAPPING`."""

    default_value = ''
    MAPPING: list[tuple] = []

    def __init__(self, **kwargs) -> None:
        self.TO_REPR = {k: v for (k, v) in self.MAPPING}
        self.FROM_REPR = {v.upper(): k for (k, v) in self.MAPPING}
        super(EnumField, self).__init__(**kwargs)

    def to_representation(self, obj: Enum) -> str:
        # We want to make sure that we always pass enums to EnumFields. If this
        # is not the case, we would otherwise silently fall back on the default
        # value.
        assert isinstance(obj, Enum)
        return self.TO_REPR.get(obj, self.default_value)

    def to_internal_value(self, obj: str) -> Enum:
        if self.required and not obj:
            raise ValidationError([self.error_messages['required']])
        try:
            return self.FROM_REPR[obj.upper()]
        except KeyError:
            raise ValidationError(f'{obj} is an invalid value for this field')


class MultipleEnumField(serializers.Field):
    """Base class to serialize fields with multiple enums."""

    MAPPING: list[tuple] = []

    def __init__(self, **kwargs) -> None:
        self.TO_REPR = {k: v for (k, v) in self.MAPPING}
        self.FROM_REPR = {v.upper(): k for (k, v) in self.MAPPING}
        super(MultipleEnumField, self).__init__(**kwargs)

    def to_representation(self, obj: list[Enum]) -> list[str]:
        itemlist = []
        for item in obj:
            itemlist.append(self.TO_REPR[item])
        return itemlist

    def to_internal_value(self, obj: list[str]) -> list[Enum]:
        if self.required and not obj:
            raise ValidationError([self.error_messages['required']])
        try:
            itemlist = []
            for item in obj:
                itemlist.append(self.FROM_REPR[item.upper()])
            return itemlist
        except KeyError:
            raise ValidationError(f'{obj} is an invalid value for this field')
