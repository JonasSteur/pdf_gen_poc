from unittest.mock import Mock

from pytest import raises

from .. import log_call


def test_returns_value() -> None:
    mock = Mock()

    @log_call(mock)
    def example():
        return 'test'

    assert example() == 'test'


def test_passes_arguments() -> None:
    mock = Mock()

    @log_call(mock)
    def example(arg):
        assert arg == 'test'

    example('test')


def test_logs_info() -> None:
    mock = Mock()

    @log_call(mock)
    def example():
        pass

    example()
    assert mock.info.called


def test_returns_exception() -> None:
    mock = Mock()

    @log_call(mock)
    def example():
        raise IOError

    with raises(IOError):
        example()


def test_set_identifier() -> None:
    mock = Mock()

    @log_call(mock, prefix='test123')
    def example():
        pass

    example()
    assert mock.info.called


def test_set_sensitive_data() -> None:
    mock = Mock()

    @log_call(mock, sensitive_data=['password'])
    def example(password):
        pass

    example(password='test')
    assert mock.info.called
