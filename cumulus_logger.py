try:
    from collections.abc import Mapping  # Python 3
except ImportError:
    from collections import Mapping  # Python 2
from datetime import datetime
from functools import reduce
import json
import logging
import sys


def _path_finder(*paths):
    """Returns a function that finds the first non-None value along the
    specified paths in a Mapping.

    The returned function takes a Mapping and an optional default value, and
    returns the first non-None value it finds while getting values from the
    specified paths within the Mapping, where each path may be a dot-separated
    string for traversing nested Mappings.  If no value is found along a path,
    the next path is checked, until either a non-None value is found or all
    paths have been checked.  If a non-None value is found, it is returned.
    Otherwise, it returns the default value, if specified, or None.

    >>> obj = {"a": 1, "x": {"y": {"z": 2}}}
    >>> _path_finder("a.b", "x.y.z")(obj)
    2
    >>> obj = {"a": 1, "x": {"y": 2}}
    >>> _path_finder("a.b", "x.y.z")(obj)  # Returns None
    >>> _path_finder("a.b", "x.y.z")(obj, 42)
    42
    """
    def _get(val, key):
        return val.get(key, None) if isinstance(val, Mapping) else None

    def _getter(obj):
        return lambda path: reduce(_get, path.split("."), obj)

    def _finder(obj, default=None):
        vals = (val for val in map(_getter(obj), paths) if val is not None)
        return next(vals, default)

    return _finder


def _extended_paths(*paths):
    extended_paths = list(paths)
    extended_paths.extend("cma.event.%s" % path for path in paths)
    return extended_paths


def _get_async_operation_id(event):
    paths = _extended_paths("cumulus_meta.asyncOperationId")
    return _path_finder(*paths)(event)


def _get_execution_name(event):
    paths = _extended_paths("cumulus_meta.execution_name")
    return _path_finder(*paths)(event)


def _get_granule_ids(event):
    paths = _extended_paths("payload.granules", "meta.input_granules")
    granules = _path_finder(*paths)(event, [])
    return list(map(_path_finder("granuleId"), granules))


def _get_parent_arn(event):
    paths = _extended_paths("cumulus_meta.parentExecutionArn")
    return _path_finder(*paths)(event)


def _get_stack_name(event):
    paths = _extended_paths("meta.stack")
    return _path_finder(*paths)(event)


def _get_exception_message(**kwargs):
    exc_info = kwargs.get('exc_info', False)
    if not exc_info:
        return ''
    if not isinstance(exc_info, tuple):
        exc_info = sys.exc_info()
    if not any(item for item in exc_info):
        return ''
    return logging.Formatter().formatException(exc_info)


class CumulusLogger:
    def __init__(self, name=__name__, level=logging.DEBUG):
        """Creates a logger with a name and loggging level."""

        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        # Avoid duplicate message in AWS cloudwatch
        self.logger.propagate = False
        if not self.logger.handlers:
            log_handler = logging.StreamHandler()
            log_handler.setLevel(logging.DEBUG)
            log_handler.setFormatter(logging.Formatter('%(message)s'))
            self.logger.addHandler(log_handler)

        self.event = None
        self.context = None
        self._msg = {}

    def setMetadata(self, event, context):
        """Sets metadata to be logged via one of the logging methods.

        Extracts the following metadata from various locations within the
        ``event`` and ``context`` parameters (indicated within parentheses):

        + ``asyncOperationId`` (``event``): asynchronous operation ID of the
          execution
        + ``executions`` (``event``): singleton list containing the execution
          name
        + ``granules`` (``event``): list of granule IDs
        + ``parentArn`` (``event``): ARN of the parent execution
        + ``sender`` (``context``): function name (or ``"unknown"``)
        + ``stackName`` (``event``): stack name
        + ``version`` (``context``): function version (or ``"unknown"``)

        See ``createMessage`` for details regarding the full message object
        created (which includes the metadata above) for logging via one of the
        logging methods.

        Arguments:
            event: Either a full Cumulus Message or a Cumulus Remote Message
            context: An AWS Lambda context object
        """
        self.event = event
        self.context = context

        granules = _get_granule_ids(event)

        # Exclude items from self._msg where values are "empty"
        self._msg = dict((k, v) for k, v in {
            "asyncOperationId": _get_async_operation_id(event),
            "executions": _get_execution_name(event),
            "granules": json.dumps(granules) if granules else None,
            "parentArn": _get_parent_arn(event),
            "sender": getattr(context, "function_name", "unknown"),
            "stackName": _get_stack_name(event),
            "version": getattr(context, "function_version", "unknown")
        }.items() if v)

    def createMessage(self, message, *args, **kwargs):
        """Returns a dict containing a string message along with metadata.

        Returns a dict containing the metadata described in ``setMetadata``, as
        well as a ``timestamp`` key mapped to the current date and time in ISO
        format, along with additional information based upon the value of the
        ``message`` parameter.  If ``message`` is a dict-like object, it is
        merged into the dict to be returned, but the metadata and ``timestamp``
        entries take precedence.  The dict-like ``message`` should also contain
        a ``message`` key mapped to a formatted message of relevance, but this
        is a convention, not a requirement.

        If ``message`` is not a dict-like object, it should conventionally be
        a string or an exception, although any non dict-like object is
        converted to a string via the ``str`` function, and is formatted via
        the ``format`` string method, passing in the ``*args`` and ``**kwargs``
        arguments supplied to this method.  Further, if ``**kwargs`` includes
        the ``exc_info`` key with a "truthy" value, the current traceback
        information is appended to the formatted message.  Finally, the
        resulting message is associated with the ``message`` key within the
        dict returned by this method.

        Args:
            message (Union[str, Mapping]): message to log
                If the message is a dict-like object, it is copied into a new
                dict to be logged.  Otherwise, the message is converted to a
                string, formatted (via the string ``format`` method) and mapped
                to the ``"message"`` key in a new dict to be logged.
            *args: additional positional arguments that may be used to format
                ``message`` via ``str(message).format(*args, **kwargs)``, but
                only if ``message`` is not a dict-like object
            **kwargs: keyword args that may be used to format ``message`` via
                ``str(message).format(*args, **kwargs)``, but only if
                ``message`` is not a dict-like object; further, if ``exc_info``
                is included as a keyword argument with a "truthy" value,
                exception information is appended to the formatted``message``

        Examples:
            The following examples are intended to illustrate how the
            ``message`` value in the logged object is affected in various ways,
            and thus, for brevity, omit the metadata described above (indicated
            by a trailing elipsis).  The comment preceding each code block
            indicates the logging level and abridged message produced by the
            code that immediately follows the comment:

            >>> event = {}
            >>> context = object()
            >>> logger = CumulusLogger()
            >>> logger.setMetadata(event, context)
            >>> message = logger.createMessage("hello world!")
            >>> message['message'], message['sender'], message['version']
            ('hello world!', 'unknown', 'unknown')

            >>> message = logger.createMessage("The answer is {}", 42)
            >>> message['message']
            'The answer is 42'

            # Note that no message formatting occurrs because a dict-like
            # object was supplied as the first argument to the method
            >>> message = logger.createMessage({"message": "The answer is {}", "answer": 42})
            >>> message['message'], message['answer']
            ('The answer is {}', 42)
        """
        msg = {}

        if isinstance(message, Mapping):
            msg.update(message)
        else:
            # - In case message is not a string (e.g., exception) use str
            # - Only call str.format() if args or kwargs are actually given, so
            #   that curly braces in the message do not cause an IndexError or
            #   KeyError here
            fmt_message = str(message)
            if args or kwargs:
                fmt_message = fmt_message.format(*args, **kwargs)

            ex_message = _get_exception_message(**kwargs)
            msg["message"] = " ".join(filter(None, [fmt_message, ex_message]))

        msg.update(self._msg)
        msg["timestamp"] = datetime.now().isoformat()

        return msg

    def log(self, message, *args, **kwargs):
        """Logs the message plus metadata at a computed logging level.

        Use of this method is discouraged because it is not obvious at which
        level the message is logged.  Instead, use one of the other methods
        (``info``, ``warn``, etc.) that explicitly names a logging level.

        If the message is a dict-like object with a ``"level"`` value that
        indicates a valid logging level name (case-insensitive), the message is
        logged at that level (e.g., ``"info"``, ``"warn"``, etc.).  Otherwise,
        the message is logged at the level specified when this logger was
        instantiated (i.e., via the ``level`` keyword argument of the
        constructor).

        Passes the supplied arguments to ``createMessage`` and logs the
        returned message dict.  See ``createMessage``.
        """
        self._log(logging.NOTSET, message, *args, **kwargs)

    def trace(self, message, *args, **kwargs):
        """Logs the message plus metadata at level ``logging.DEBUG``.

        There is no ``TRACE`` level defined in the standard logging module, but
        this is implemented for consistency with CMA clients implemented in
        other languages where such a level is defined (and is intended to be
        more verbose than ``DEBUG``).

        Passes the supplied arguments to ``createMessage`` and logs the
        returned message dict.  See ``createMessage``.
        """
        self.debug(message, *args, **kwargs)

    def debug(self, message, *args, **kwargs):
        """Logs the message plus metadata at level ``logging.DEBUG``.

        Passes the supplied arguments to ``createMessage`` and logs the
        returned message dict.  See ``createMessage``.
        """
        self._log(logging.DEBUG, message, *args, **kwargs)

    def info(self, message, *args, **kwargs):
        """Logs the message plus metadata at level ``logging.INFO``.

        Passes the supplied arguments to ``createMessage`` and logs the
        returned message dict.  See ``createMessage``.
        """
        self._log(logging.INFO, message, *args, **kwargs)

    def warn(self, message, *args, **kwargs):
        """Logs the message plus metadata at level ``logging.WARN``.

        Passes the supplied arguments to ``createMessage`` and logs the
        returned message dict.  See ``createMessage``.
        """
        self._log(logging.WARN, message, *args, **kwargs)

    def warning(self, message, *args, **kwargs):
        """Logs the message plus metadata at level ``logging.WARN``.

        Passes the supplied arguments to ``createMessage`` and logs the
        returned message dict.  See ``createMessage``.
        """
        self.warn(message, *args, **kwargs)

    def error(self, message, *args, **kwargs):
        """Logs the message plus metadata at level ``logging.ERROR``.

        Passes the supplied arguments to ``createMessage`` and logs the
        returned message dict.  See ``createMessage``.
        """
        self._log(logging.ERROR, message, *args, **kwargs)

    def fatal(self, message, *args, **kwargs):
        """Logs the message plus metadata at level ``logging.CRITICAL``.

        Passes the supplied arguments to ``createMessage`` and logs the
        returned message dict.  See ``createMessage``.
        """
        self.critical(message, *args, **kwargs)

    def critical(self, message, *args, **kwargs):
        """Logs the message plus metadata at level ``logging.CRITICAL``.

        Passes the supplied arguments to ``createMessage`` and logs the
        returned message dict.  See ``createMessage``.
        """
        self._log(logging.CRITICAL, message, *args, **kwargs)

    def _resolve_log_level(self, level_name):
        if not isinstance(level_name, str):
            return self.logger.level
        level = logging.getLevelName(level_name.upper())
        return level if isinstance(level, int) else self.logger.level

    def _log(self, level, message, *args, **kwargs):
        msg = self.createMessage(message, *args, **kwargs)
        if level == logging.NOTSET or not isinstance(level, int):
            level = self._resolve_log_level(msg.get("level", None))
        msg["level"] = logging.getLevelName(level).lower()
        self.logger.log(level, json.dumps(msg))


if __name__ == "__main__":
    import doctest
    doctest.testmod()
