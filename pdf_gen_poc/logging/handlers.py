from logging import Handler

from django_statsd.clients import statsd


class StatsdHandler(Handler):
    """Send error to statsd"""

    def __init__(self, statsd_key):
        Handler.__init__(self)

        self.statsd_key = statsd_key

    def emit(self, record):
        statsd.incr(self.statsd_key)
