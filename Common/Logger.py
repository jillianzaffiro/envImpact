from datetime import datetime
from structlog import get_logger


class LoggingMiddleware(object):
    """Logging Middleware that injects global logging to all API requests."""
    def __init__(self, log, app):
        self.log = log
        self.app = app

    def __call__(self, environ, start_response):
        self.log.info('Route {} called.'.format(environ['RAW_URI']))
        return self.app(environ, start_response)


class Logger:
    def __init__(self, preamble):
        self.preamble = preamble
        self._lgr = get_logger()
        self.info("Starting logging subsystem")

    def warn(self, msg):
        self._send("WARNING", msg)

    def info(self, msg):
        self._send("INFO", msg)

    def stats(self, msg):
        self._send("STATS", msg)

    def error(self, msg):
        self._send("ERROR", msg)

    def _send(self, m_type, msg):
        if self._lgr is None:
            print(f"{datetime.now()}: {self.preamble}-{m_type}:{msg}")
        else:
            self._send_raw(f"{self.preamble}-{m_type}:{msg}")

    def _send_raw(self, msg):
        self._lgr.msg(msg)
