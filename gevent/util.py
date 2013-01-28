# Copyright (c) 2009 Denis Bilenko. See LICENSE for details.
__all__ = ['wrap_errors']

import sys
import traceback

import logging
_log = logging.getLogger(__name__)
ch = logging.StreamHandler()
_log.addHandler(ch)

class Log(object):

    def __init__(self, log='default'):
        if log == 'default':
            self._log = _log
        else:
            self._log = log

    def __getattr__(self, name):
        if len(logging.root.handlers) > 0:
            if name == 'log':
                if isinstance(self._log, logging.Logger):
                    return self.log_logging
                else:
                    return self.log_stderr
        else:
            return self.log_stderr
        raise AttributeError()

    def log_logging(self, msg):
        if isinstance(self._log, logging.Logger) is False:
            self.log_stderr(msg)
            return
        _log.warn(msg)
        
    def log_stderr(self, msg):
        msg = "%s\n" % msg
        sys.stderr.write(msg)

    def exception(self, msg):
        if isinstance(self._log, logging.getLogger) is False:
            traceback.print_exc()
            return
        _log.exception(msg)

class wrap_errors(object):
    """Helper to make function return an exception, rather than raise it.

    Because every exception that is unhandled by greenlet will be logged,
    it is desirable to prevent non-error exceptions from leaving a greenlet.
    This can done with simple ``try``/``except`` construct::

        def wrapped_func(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except (A, B, C), ex:
                return ex

    :class:`wrap_errors` provides a shortcut to write that in one line::

        wrapped_func = wrap_errors((A, B, C), func)

    It also preserves ``__str__`` and ``__repr__`` of the original function.
    """
    # QQQ could also support using wrap_errors as a decorator

    def __init__(self, errors, func):
        """Make a new function from `func', such that it catches `errors' (an
        Exception subclass, or a tuple of Exception subclasses) and return
        it as a value.
        """
        self.errors = errors
        self.func = func

    def __call__(self, *args, **kwargs):
        func = self.func
        try:
            return func(*args, **kwargs)
        except self.errors:
            return sys.exc_info()[1]

    def __str__(self):
        return str(self.func)

    def __repr__(self):
        return repr(self.func)

    def __getattr__(self, item):
        return getattr(self.func, item)
