# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
import os
import sys
from functools import partial
from io import StringIO
from subprocess import PIPE
from subprocess import check_output

# absolute_import ensure "import logging" will not import the logging package from the
# current module but the system wide package

log = logging.getLogger(__name__)

# flake8: noqa
# pylint: disable=too-many-locals,bare-except


def setup_logging(split=True,
                  unbuffered=False,
                  debug=False,
                  module_verbose=False,
                  fmt=None,
                  force_no_tty=None):
    '''
    :param split: preserve log headers for multiline strings, and adapt to the current terminal
                  witdh if applicable
    :param unbuffered: ask the stdout to avoid buffering to send logs as fast as possible to the
                       caller script, only when not inside a TTY
    :param debug: enable debug level
    :param module_verbose: add module (file, line number) to each log line
    :param fmt: overwrite the formatter
    :param force_no_tty: force the usage of the no TTY formatter
    '''
    try:
        # Note: colorlog is not a 'requirement' of slavescripts (and shouldn't!), so it might not be
        # installed. In this case, normal logging formatter is used. But if available, let's print
        # plentful of colors!
        #
        # To install it, simply do:
        #
        #    pip install colorlog
        from colorlog import ColoredFormatter
    except:
        ColoredFormatter = None  # pylint: disable=invalid-name

    # this logging config will output debug and info to stdout and warning, error, and critical to
    # stderr, so that buildbot can color them
    # logs with level > will go to stderr, with level < will go to stdout
    stderr_threshold = logging.WARNING
    # logs with level < will be hidden
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
    if fmt:
        ColoredFormatter = None  # pylint: disable=invalid-name
        fmt_nocolor_str = fmt
    else:
        if module_verbose:
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

        if debug:
            fmt_color_str = fmt_debug_color_str
            fmt_nocolor_str = fmt_debug_nocolor_str
        else:
            fmt_color_str = fmt_simple_color_str
            fmt_nocolor_str = fmt_simple_nocolor_str

    if debug:
        default_level = logging.DEBUG
    else:
        default_level = logging.INFO

    logging.basicConfig(stream=sys.stdout, level=default_level, format=fmt_nocolor_str)

    date_fmt_string = None
    # Replace the default formatter because it is buggy
    root = logging.getLogger()
    # Do *not* replace the formatter in quiet mode since we want to bare output

    term_width = -1
    if split:
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

    if force_no_tty:
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
    return root.handlers[0]
