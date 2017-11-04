# coding: utf-8

import logging
import os
import sys
from enum import Enum
from functools import partial
from io import StringIO
from logging.handlers import RotatingFileHandler
from subprocess import PIPE
from subprocess import check_output

log = logging.getLogger(__name__)

# flake8: noqa
# pylint: disable=too-many-locals,bare-except


class OutputType(Enum):
    PLAIN = 1
    DEV = 2
    JSON = 3


g_file_handler = None
g_stream_handler = None


def setup_logging(outputtype=OutputType.PLAIN,
                  debug=False,
                  unbuffered=False,
                  logfile=None,
                  dev_allow_colors=True,
                  dev_split=True,
                  dev_module_verbose=True,
                  dev_force_fmt=None,
                  dev_force_no_tty=None):
    '''
    :param outputtype: one of the following:
                         - OutputType.PLAIN: plain log output (all in stdout)
                         - OutputType.DEV: developer-friendly, multi-columns, colored output
                                           (if `colorlog` package is available and
                                           `dev_allow_colors` set to True)
                         - OutputType.JSON: output in json format, 1 json-chunk per line
    :param debug: configure log level. Can take the following values:
                    - False: logs will be in level logging.INFO
                    - True: logs will be in level logging.DEBUG
                    - logging.[DEBUG|INFO|WARNING|ERROR|FATAL]: set log level manually
    :param unbuffered: ask the stdout to avoid buffering to send logs as fast as possible to the
                       caller script.
                       Only available when not inside a TTY, especially for pipeline of logs.
                       This also trigger the split of outputs into stdout and stderr:
                           >=logging.ERROR, logs go to stderr
                           < logging.ERROR, logs go to stdout
    :param logfile: enable output of logs to a file
    The rest of the parameters allow to fine-tune developer-mode
    :param dev_allow_colors: allow log coloration if `colorlog` is installed
    :param dev_split: preserve log headers for multiline strings, and adapt to the current terminal
                  witdh if applicable
    :param dev_module_verbose: add module (file, line number) to each log line
    :param dev_force_fmt: overwrite the formatter
    :param dev_force_no_tty: force the usage of the no TTY formatter
    '''
    ColoredFormatter = False  # pylint: disable=invalid-name
    if dev_allow_colors:
        try:
            # Note: colorlog is not a 'requirement' of your application (and shouldn't!),
            # so it might not be installed.
            # In this case, normal logging formatter is used.
            # But if available, let's print plentful of colors!
            #
            # To install it, simply do:
            #
            #    pip install colorlog
            #
            from colorlog import ColoredFormatter
        except:
            pass

    # this logging config will output debug and info to stdout and warning, error, and critical to
    # stderr, so that consumer can color them if needed
    # logs with `level > stderr_threshold` will go to `stderr`,
    # logs with `level < stderr_threshold` will go to `stdout`
    stderr_threshold = logging.WARNING
    # logs with `level < stdout_level` will be hidden
    stdout_level = logging.DEBUG

    class InfoFilter(logging.Filter):
        def filter(self, record):
            return record.levelno < stderr_threshold

    class SplitFormatterMixin(object):
        '''
        Magic Formatter that gracefully handle multiline logs, ie it split the multiline string
        and add each log independently.

        This handles two spliting:

        - if the terminal width is found, try to fit the output in the terminal by splitting the
          string arbitrarily
        - if the record message is multiline, split it and print prefix (loglevel, date,...)
          independently

        Note this only impacts the display to stdout handler, not the record storage, so
        if these logs are sent to another handler (for instance to splunk handler), the log
        will not be split
        '''

        def format(self, record):
            record.message = record.getMessage()
            record.msg = record.message
            if record.args:
                record.args = ()
            if self.usesTime():
                record.asctime = self.formatTime(record, self.datefmt)
            multiline_message = record.message
            formatted_lines = []
            if not self.split:
                s = self._get_formated_line(record)
                formatted_lines.append(s)
            else:
                for line in multiline_message.split("\n"):
                    if self.term_width < 1:
                        sublines = [line]
                    else:
                        sublines = [
                            l for l in iter(partial(StringIO(line).read, int(self.term_width)), '')
                        ]
                    if not sublines:
                        # If the string is empty, still add an empty record in the output
                        record.message = ""
                        record.msg = ""
                        s = self._get_formated_line(record)
                        formatted_lines.append(s)
                    else:
                        for subline in sublines:
                            record.message = subline
                            record.msg = subline
                            s = self._get_formated_line(record)
                            formatted_lines.append(s)
            return "\n".join(formatted_lines)

        def _get_formated_line(self, record):
            s = self._get_record_with_fmt(record)
            if record.exc_info:
                # Cache the traceback text to avoid converting it multiple times
                # (it's constant anyway)
                if not record.exc_text:
                    record.exc_text = self.formatException(record.exc_info)
            if record.exc_text is not None:
                if s and s[-1:] != "\n":
                    s = s + "\n"
                try:
                    s = s + record.exc_text
                except UnicodeError:
                    # Sometimes filenames have non-ASCII chars, which can lead
                    # to errors when s is Unicode and record.exc_text is str
                    # See issue 8924.
                    # We also use replace for when there are multiple
                    # encodings, e.g. UTF-8 for the filesystem and latin-1
                    # for a script. See issue 13232.
                    s = s + record.exc_text.decode(sys.getfilesystemencoding(), 'replace')
            return s

    class SplitFormatter(SplitFormatterMixin, logging.Formatter):
        def __init__(self, fmt=None, datefmt=None, term_width=-1, split=True):
            super(SplitFormatter, self).__init__(fmt, datefmt)
            self.term_width = term_width
            self.split = split

        def _get_record_with_fmt(self, record):
            return self._fmt % record.__dict__

    if ColoredFormatter:

        class SplitColorFormatter(SplitFormatterMixin, ColoredFormatter):
            def __init__(self, fmt=None, datefmt=None, term_width=-1, split=True, log_colors=None):
                super(SplitColorFormatter, self).__init__(fmt, datefmt, log_colors=log_colors)
                self.term_width = term_width
                self.split = split

            def _get_record_with_fmt(self, record):
                return ColoredFormatter.format(self, record)

    align_level_width = 8
    extra_char_width = 3
    if outputtype == OutputType.PLAIN:
        fmt_color_str = fmt_nocolor_str = "%(message)s"
    elif outputtype == OutputType.DEV:
        if dev_force_fmt:
            fmt_nocolor_str = dev_force_fmt
        else:
            if dev_module_verbose:
                fmt_module_nocolor_str = "[%(name)-37.37s] "
                fmt_module_color_str = ("[%(yellow)s%(name)-37.37s%(reset)s] ")
            else:
                fmt_module_nocolor_str = ""
                fmt_module_color_str = ""
            fmt_debug_nocolor_str = (
                '%(asctime)19.19ss ' + fmt_module_nocolor_str + '%(levelname)7s: %(message)s')
            fmt_debug_color_str = (
                '%(blue)s%(asctime)19.19s%(reset)s ' + fmt_module_color_str +
                '%(log_color)s%(levelname)-7s%(reset)s | ' + '%(log_color)s%(message)s%(reset)s')

            fmt_simple_nocolor_str = '%(levelname)-7s - ' + fmt_module_nocolor_str + '%(message)s'
            fmt_simple_color_str = (
                '%(log_color)s' + fmt_module_color_str + '[%(levelname).1s]%(reset)s %(log_color)s'
                '%(message)s%(reset)s')

            if debug is True:
                fmt_color_str = fmt_debug_color_str
                fmt_nocolor_str = fmt_debug_nocolor_str
            else:
                fmt_color_str = fmt_simple_color_str
                fmt_nocolor_str = fmt_simple_nocolor_str
    elif outputtype == OutputType.JSON:
        raise NotImplementedError()

    if debug is True:
        default_level = logging.DEBUG
    elif debug is False:
        default_level = logging.INFO
    else:
        assert debug in [
            logging.CRITICAL,
            logging.ERROR,
            logging.WARNING,
            logging.INFO,
            logging.DEBUG,
        ], "invalid debug (neither True/False neither a logging level)"
        default_level = debug

    logging.basicConfig(stream=sys.stdout, level=default_level, format=fmt_nocolor_str)

    date_fmt_string = None
    # Replace the default formatter because it is buggy
    root = logging.getLogger()
    # Do *not* replace the formatter in quiet mode since we want to bare output

    # force log level on root, in case of multiple call of basicConfig, if the first level
    # was higher than the second, the root log level is not not updated
    root.setLevel(default_level)
    assert log.getEffectiveLevel() == default_level, "invalid log level set on root !"

    term_width = -1
    if dev_split:
        # Try to retrieve the terminal width:
        term_width = -1
        try:
            # redirecting the stderr to an unused PIPE, to avoid the following issue:
            #     'stty: standard input: Invalid argument'
            # when executed from a step ShellCommand
            data = check_output(['stty', 'size'], stderr=PIPE)
            _, columns = data.split()
            if columns > 0:
                term_width = columns
        except:
            pass
        term_width = (int(term_width) - align_level_width - extra_char_width)
    # disable terminal spliting for the moment
    term_width = -1

    if dev_force_no_tty:
        is_tty = False
    else:
        is_tty = sys.stdout.isatty()

    if not is_tty:
        # We are in Buildbot or in a pipe, don't use colorlog!
        ColoredFormatter = None  # pylint: disable=invalid-name
    if not ColoredFormatter:
        formatter = SplitFormatter(fmt_nocolor_str, term_width=term_width, split=True)
    else:
        formatter = SplitColorFormatter(
            fmt_color_str,
            date_fmt_string,
            term_width=term_width,
            split=True,
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'red,bg_white',
            })

    global g_file_handler
    global g_stream_handler

    if unbuffered and not is_tty:
        root.handlers = []
        # Make stdout unbuffered, so that we get output asap to buildbot log
        sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)
        sys.stderr = os.fdopen(sys.stderr.fileno(), 'w', 0)
        h1 = logging.StreamHandler(sys.stdout)
        h1.setLevel(stdout_level)
        h1.setFormatter(formatter)
        h1.addFilter(InfoFilter())
        h2 = logging.StreamHandler(sys.stderr)
        h2.setFormatter(formatter)
        h2.setLevel(stderr_threshold)

        # Don't print useless info about "New connection" + security warnings
        logging.getLogger("requests.packages.urllib3.connectionpool").setLevel(logging.ERROR)

        logging.getLogger().addHandler(h1)
        logging.getLogger().addHandler(h2)
        logging.getLogger().setLevel(logging.NOTSET)
    else:
        root.handlers[0].setFormatter(formatter)

    if logfile:
        log.debug("Also output logs to file: %s", logfile)
        file_fmt = " :: ".join(
            ["%(asctime)s", "%(levelname)s", "%(pathname)s:%(lineno)s", "%(message)s"])
        file_formatter = logging.Formatter(file_fmt)
        file_handler = RotatingFileHandler(str(logfile), 'a', 5 * 1024 * 1024, 1)
        file_handler.setFormatter(file_formatter)
        if g_file_handler:
            root.removeHandler(g_file_handler)
        root.addHandler(file_handler)
        g_file_handler = file_handler
