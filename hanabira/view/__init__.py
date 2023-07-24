# -*- coding: utf-8 -*-

from pylons import tmpl_context as c, request, response, session, app_globals as g
from pylons.i18n import _, ungettext, N_, get_lang, set_lang

from hanabira.lib.decorators import getargspec, make_args_for_spec

from .error import *
from .post import PostView, PostAPIView
from .post_revisions import PostRevisionsView
from .thread import ThreadView, ThreadAPIView
from .board import BoardView, BoardsView
from .usersession import UserSessionView
from .data import DataView, result_false, result_true
from .mako import MakoView
from .base import BaseView

from .admin.posts_list import AdminPostsListView

import logging
log = logging.getLogger(__name__)

class HTMLView(BaseView):
    def __init__(self, h):
        self.html = h
    def make_xhtml(self):
        return self.html

def render_view(func):
    spec = getargspec(func)
    def _decorator(self, **kw):
        ## Use xhtml as default for now
        format = kw.get('format', 'xhtml')
        if not format:
            log.warn(u"Call without format! Fn: {0}".format(func))
        args = make_args_for_spec(spec, kw)
        view = func(self, **args)
        return view.render(format)
    return _decorator