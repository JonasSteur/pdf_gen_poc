from rest_framework import serializers

from .fields import BadRequestErrorCodeField, FieldErrorCodeField


class FieldErrorDetailsSerializer(serializers.Serializer):
    code = FieldErrorCodeField(read_only=True)
    message = serializers.CharField(read_only=True, required=False)


class FieldErrorSerializer(serializers.Serializer):
    field = serializers.CharField(read_only=True)
    error_details = FieldErrorDetailsSerializer(read_only=True, many=True)

    def to_representation(self, instance: dict):
        value = super().to_representation(instance)
        value['errors'] = value.pop('error_details')
        return value


class BadRequestResponseSerializer(serializers.Serializer):
    code = BadRequestErrorCodeField(read_only=True)
    message = serializers.CharField(read_only=True)
    incorrect_fields = FieldErrorSerializer(read_only=True, many=True, required=False)
