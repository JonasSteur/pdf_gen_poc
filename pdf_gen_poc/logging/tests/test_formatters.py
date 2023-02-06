from json import loads
from logging import INFO, LogRecord
from sys import exc_info

from ..formatters import JSONFormatter

formatter = JSONFormatter()


def test_format() -> None:
    record = LogRecord('test', INFO, '', 1, 'test', (), None)
    json = loads(formatter.format(record))
    assert json['message'] == record.getMessage()


def test_exc_info() -> None:
    try:
        raise Exception('test')
    except Exception:
        (exc1, exc2, exc3) = exc_info()
        assert exc1 and exc2 and exc3
        record = LogRecord('test', INFO, '', 1, 'test', (), (exc1, exc2, exc3))

    json = loads(formatter.format(record))
    assert 'exc_info' in json


def test_extra() -> None:
    record = LogRecord('test', INFO, '', 1, 'test', (), None)
    record.__dict__['test_attr'] = 'hello'
    json = loads(formatter.format(record))
    assert json['test_attr'] == 'hello'


def test_skip_not_serialisable() -> None:
    class A(object):
        def __init__(self):
            pass

    record = LogRecord('test', INFO, '', 1, 'test', (), None)
    record.__dict__['test_attr'] = A()
    json = loads(formatter.format(record))
    assert 'test_attr' not in json
