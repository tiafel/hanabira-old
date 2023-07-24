# (c) 2005 Ian Bicking and contributors; written for Paste (http://pythonpaste.org)
# Licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php

import smtplib
import ssl
import time
from weberror import formatter
from email.utils import formatdate

class Reporter(object):

    def __init__(self, **conf):
        for name, value in list(conf.items()):
            if not hasattr(self, name):
                raise TypeError(
                    "The keyword argument %s was not expected"
                    % name)
            setattr(self, name, value)
        self.check_params()

    def check_params(self):
        pass

    def format_date(self, exc_data):
        return time.strftime('%c', exc_data.date)

    def format_html(self, exc_data, **kw):
        return formatter.format_html(exc_data, **kw)

    def format_text(self, exc_data, **kw):
        return formatter.format_text(exc_data, **kw)

class EmailReporter(Reporter):
    pass

class LogReporter(Reporter):

    filename = None
    show_hidden_frames = True

    def check_params(self):
        assert self.filename is not None, (
            "You must give a filename")

    def report(self, exc_data):
        text, head_text = self.format_text(
            exc_data, show_hidden_frames=self.show_hidden_frames)
        f = open(self.filename, 'a')
        try:
            f.write(text + '\n' + '-'*60 + '\n')
        finally:
            f.close()

class FileReporter(Reporter):

    file = None
    show_hidden_frames = True

    def check_params(self):
        assert self.file is not None, (
            "You must give a file object")

    def report(self, exc_data):
        text, head_text = self.format_text(
            exc_data, show_hidden_frames=self.show_hidden_frames)
        self.file.write(text + '\n' + '-'*60 + '\n')

class WSGIAppReporter(Reporter):

    def __init__(self, exc_data):
        self.exc_data = exc_data

    def __call__(self, environ, start_response):
        start_response('500 Server Error', [('Content-type', 'text/html')])
        return [formatter.format_html(self.exc_data)]

def as_str(v):
    if isinstance(v, str):
        return v
    if not isinstance(v, str):
        v = str(v)
    if isinstance(v, str):
        v = v.encode('utf8')
    return v
