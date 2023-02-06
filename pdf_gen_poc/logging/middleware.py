from collections.abc import Callable
from json import JSONDecodeError, loads
from logging import Logger, getLogger
from typing import Any

from django.http import HttpRequest, HttpResponse
from django_statsd.clients import statsd
from waffle import switch_is_active

from . import local_thread, obfuscate_sensitive_args

default_logger = getLogger(__name__)
Responder = Callable[[HttpRequest], HttpResponse]

WRITE_METHODS = ['POST', 'PUT', 'PATCH', 'DELETE']
LOG_BODY = 'logging:log_body'
LOG_BAD_REQUEST_RESPONSE = 'logging:log_bad_request_response'
LOG_ACCESS_TOKEN = 'logging:access_token'
SENSITIVE_WORDS = ['password']


def _log_body(extra: dict[str, Any], response: HttpResponse, request: HttpRequest) -> None:
    if switch_is_active(LOG_BODY) and 400 <= response.status_code < 500 and request.method in WRITE_METHODS:
        if request.content_type == 'application/json':
            try:
                body = loads(request.body)
                extra['body'] = obfuscate_sensitive_args(SENSITIVE_WORDS, body)
            except JSONDecodeError:
                statsd.incr('bad_request.invalid_json')
                body = str(request.body)
                default_logger.info(
                    'Invalid json in body: %s',
                    '*** (contains sensitive word)' if any(w in body for w in SENSITIVE_WORDS) else body,
                )
        if request.content_type == 'application/x-www-form-urlencoded':
            if '/oauth2/' in request.path:
                extra['body'] = {'oauth2 request'}
            else:
                default_logger.info('Invalid content type')


def _log_bad_request_response(extra: dict[str, Any], response: HttpResponse) -> None:
    if switch_is_active(LOG_BAD_REQUEST_RESPONSE) and response.status_code == 400:
        extra['response'] = response.content


def save_request_body(get_response: Responder) -> Responder:  # pragma: no cover
    """
    Save the body of the request. If we don't do this, it won't be accessible outside DRF anymore, and we want to use
    it for logging.

    The reason for this is that Django only allows reading the request body once. This works by accessing request.body,
    which reads the request body and saves it in a private variable. Further calls to request.body will then use the
    value from the variable. It's necessary, because rest-framework accesses it in a different way, which doesn't save
    the value, and therefore makes it unavailable unless you have the DRF request object, which is not the case in
    our middleware.
    """

    def middleware(request: HttpRequest) -> HttpResponse:
        non_cacheable_types = ('application/x-www-form-urlencoded', 'multipart/form-data', 'application/octet-stream')
        content_type = request.META.get('CONTENT_TYPE', '')
        if not any(non_cacheable_type in content_type for non_cacheable_type in non_cacheable_types):
            request.body
        return get_response(request)

    return middleware


def request_log(get_response: Responder, logger: Logger = default_logger) -> Responder:
    def middleware(request: HttpRequest) -> HttpResponse:
        auth_token = request.META.get('HTTP_AUTHORIZATION')

        extra = {}

        if auth_token is not None and switch_is_active(LOG_ACCESS_TOKEN):
            extra['token'] = auth_token[7:15]

        response = get_response(request)

        extra['status_code'] = str(response.status_code)
        extra['content-length'] = str(len(response.content))
        _log_body(extra, response, request)
        _log_bad_request_response(extra, response)
        logger.info('Request %s %s', request.method, request.path, extra=extra)

        try:
            del local_thread.impersonation
        except AttributeError:
            pass

        return response

    return middleware


def request_id(get_response: Responder) -> Responder:  # pragma: no cover: the threading does not work well in tests
    """
    Parse request_id headers, save the id in the thread locals, and output the id as well.
    """

    def middleware(request):
        parsed_request_id = request.META.get('HTTP_X_REQUEST_ID')
        local_thread.request_id = parsed_request_id
        request.id = parsed_request_id

        response = get_response(request)

        if parsed_request_id:
            response['X-Request-Id'] = parsed_request_id

        try:
            del local_thread.request_id
        except AttributeError:
            pass

        return response

    return middleware
