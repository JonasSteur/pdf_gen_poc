from pdf_gen_poc.fields import EnumField, MultipleEnumField

from .objects import BadRequestErrorCode, FieldErrorCode


class FieldErrorCodeField(EnumField):
    MAPPING = [(e, e.value) for e in FieldErrorCode]


class BadRequestErrorCodeField(MultipleEnumField):
    MAPPING = [(e, e.value) for e in BadRequestErrorCode]
