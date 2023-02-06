from collections.abc import Callable, Mapping
from functools import wraps
from inspect import signature
from threading import local
from time import time
from typing import Any, Optional, TypeVar, cast

from django_statsd.clients import statsd

TFun = TypeVar('TFun', bound=Callable[..., Any])

local_thread = local()


def obfuscate_sensitive_args(sensitive_data: list[str], arguments: Any) -> Any:
    if isinstance(arguments, Mapping):
        sanitized_kwargs: dict[Any, Any] = {}
        for k, v in arguments.items():
            sanitized_kwargs[k] = '***' if k in sensitive_data else obfuscate_sensitive_args(sensitive_data, v)
        return sanitized_kwargs
    elif isinstance(arguments, list):
        sanitized_args: list[Any] = []
        for argument in arguments:
            sanitized_args.append(obfuscate_sensitive_args(sensitive_data, argument))
        return sanitized_args
    return arguments


class log_call:  # noqa: N801
    """
    A decorator to log the time and arguments of a function call

    Before logging, it will overwrite all sensitive_data of passed
    kwargs with '***' e.g. password.

    Note that sensitive data could also be inside object, but this is
    matter of implementation of __str__
    """

    def __init__(self, logger, prefix: Optional[str] = None, sensitive_data: Optional[list[str]] = None) -> None:
        self.logger = logger
        self.prefix = prefix
        self.sensitive_data = sensitive_data

    def __call__(self, method: TFun) -> TFun:
        logger = self.logger
        prefix = self.prefix
        sensitive_data = self.sensitive_data

        @wraps(method)
        def inner(*args: Any, **kwargs: Any) -> Any:
            # Inspect method name to avoid duplication
            log_name = f'{prefix}.{method.__name__}'

            # Merge args and kwargs in to a single dictionary. Now we
            # can censor sensitive arguments even if they are passed
            # as positional arguments.
            all_args = signature(method).bind(*args, **kwargs).arguments
            censored_args = obfuscate_sensitive_args(sensitive_data or [], all_args)
            logged_args = ', '.join(f'{k}={repr(v)}' for k, v in censored_args.items())

            start = time()
            try:
                with statsd.timer(log_name):
                    result = method(*args, **kwargs)
            except Exception as e:
                logger.info('Call %s(%s) with exception = %s, took %s s', log_name, logged_args, e, time() - start)
                raise e
            else:
                logger.info('Call %s(%s) with successful result, took %.3f s', log_name, logged_args, time() - start)
            return result

        return cast(TFun, inner)
