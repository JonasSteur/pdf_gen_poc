from collections.abc import Set
from datetime import datetime
from json import dumps
from logging import Formatter, LogRecord, makeLogRecord
from typing import Any

from rest_framework.utils.encoders import JSONEncoder

RECORD_KEYS: Set[str] = vars(makeLogRecord({})).keys()


def _json_serialisable(value: Any) -> bool:
    try:
        dumps(value, cls=JSONEncoder)
    except TypeError:
        return False
    else:
        return True


class JSONFormatter(Formatter):
    def format(self, record: LogRecord) -> str:
        data = {
            'timestamp': str(datetime.utcfromtimestamp(record.created)),
            'logger': record.name,
            'module': record.module,
            'message': record.getMessage(),
            'level': record.levelno,
            'request_id': getattr(record, 'request_id', None),
            'celery_task_id': getattr(record, 'celery_task_id', None),
        }

        if record.exc_info and all(record.exc_info):
            data['exc_info'] = self.formatException(record.exc_info)

        # Record any attributes passed with 'extra' kwarg that are JSON-serialisable
        data.update({k: v for k, v in vars(record).items() if k not in RECORD_KEYS and _json_serialisable(v)})

        return dumps(data, cls=JSONEncoder)
