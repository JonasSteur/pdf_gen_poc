from unittest.mock import patch

from ..handlers import StatsdHandler


def test_statsd_handler() -> None:
    handler = StatsdHandler('test')

    with patch('pdf_gen_poc.logging.handlers.statsd') as statsd_mock:
        handler.emit(None)

    statsd_mock.incr.assert_called_once_with('test')
