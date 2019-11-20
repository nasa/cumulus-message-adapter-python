import json
import logging
from datetime import datetime
import sys


def _get_exception_message(**kwargs):
    exception_str = ''
    if kwargs.get('exc_info', False):
        exception_info = kwargs['exc_info'] if isinstance(
            kwargs['exc_info'], tuple) else sys.exc_info()
        exception_str = ' ' + logging.Formatter().formatException(exception_info)
    return exception_str


def _get_execution_name(event):
    if event.get('cma'):
        return event['cma']['event']['cumulus_meta']['execution_name']
    return event['cumulus_meta']['execution_name']


class CumulusLogger(object):
    def __init__(self, name=__name__, level=logging.DEBUG):
        """
        Initialize the logger with an optional name and an optional level.
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        # avoid duplicate message in AWS cloudwatch
        self.logger.propagate = False

        log_handler = logging.StreamHandler()
        log_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(message)s')
        log_handler.setFormatter(formatter)
        self.logger.handlers = []
        self.logger.addHandler(log_handler)
        self.event = {}
        self.function_name = 'unknown'
        self.function_version = 'unknown'

    def setMetadata(self, event, context):
        """
        Log messages with contextual info needed by Cumulus.

        Arguments:
            cumulus_message -- required. either a full Cumulus Message or a
                Cumulus Remote Message
            context -- an AWS Lambda context dict
        """
        self.event = event
        self.function_name = context.function_name if hasattr(
            context, 'function_name') else 'unknown'
        self.function_version = context.function_version if hasattr(
            context, 'function_version') else 'unknown'

    def createMessage(self, message, *args, **kwargs):
        if isinstance(message, str):
            msg = {
                "message": (message.format(*args, **kwargs) +
                            _get_exception_message(**kwargs))
            }
        else:
            msg = message
        try:
            msg["level"]
        except KeyError:
            msg["level"] = "info"

        msg["executions"] = [_get_execution_name(self.event)]
        msg["timestamp"] = datetime.now().isoformat()
        msg["sender"] = self.function_name
        msg["version"] = self.function_version
        return msg

    def log(self, message, *args, **kwargs):
        self.logger.log(
            logging.INFO,
            json.dumps(self.createMessage(message, *args, **kwargs)))

    def debug(self, message, *args, **kwargs):
        msg = self.createMessage(message, *args, **kwargs)
        msg["level"] = "debug"
        self.logger.debug(json.dumps(msg))

    def info(self, message, *args, **kwargs):
        msg = self.createMessage(message, *args, **kwargs)
        msg["level"] = "info"
        self.logger.info(json.dumps(msg))

    def warn(self, message, *args, **kwargs):
        msg = self.createMessage(message, *args, **kwargs)
        msg["level"] = "warn"
        self.logger.warning(json.dumps(msg))

    def warning(self, message, *args, **kwargs):
        self.warn(message, *args, **kwargs)

    def error(self, message, *args, **kwargs):
        msg = self.createMessage(message, *args, **kwargs)
        msg["level"] = "error"
        self.logger.error(json.dumps(msg))

    def fatal(self, message, *args, **kwargs):
        msg = self.createMessage(message, *args, **kwargs)
        msg["level"] = "fatal"
        self.logger.error(json.dumps(msg))

    def trace(self, message, *args, **kwargs):
        msg = self.createMessage(message, *args, **kwargs)
        msg["level"] = "trace"
        self.logger.critical(json.dumps(msg))
