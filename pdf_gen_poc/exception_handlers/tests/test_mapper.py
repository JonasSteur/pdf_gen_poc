from typing import Any

from pytest import raises

from .. import ErrorMapper
from ..exceptions import ExternalServiceUnavailable, InvalidToken, UnknownError


def test_error_mapper_no_error():
    with ErrorMapper({InvalidToken: ExternalServiceUnavailable()}):
        pass


def test_error_mapper_mapping_found():
    with raises(ExternalServiceUnavailable):
        with ErrorMapper({InvalidToken: ExternalServiceUnavailable()}):
            raise InvalidToken


def test_error_mapper_no_mapping(caplog: Any):
    with raises(UnknownError):
        with ErrorMapper({}):
            raise UnknownError
    assert 'UnknownError' in caplog.text
