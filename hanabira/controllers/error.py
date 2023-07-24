# -*- coding: utf-8 -*-
import os.path
import random
import urllib

from paste.urlparser import PkgResourcesParser
from pylons.controllers.util import forward
from pylons.middleware import error_document_template
from webhelpers.html.builder import literal
from hanabira.lib.base import *

import logging
log = logging.getLogger(__name__)

class ErrorController(BaseController):
    def __before__(self):
        self.init_request()
        c.channel  = g.boards.get(host=request.environ['HTTP_HOST'])
        c.pageinfo = PageInfo(g.settings)
        
    def document(self):
        s = request.environ.get('beaker.session', {})
        c.admin = s.get('admin', None)
        c.scroll_threads = 0
        orig_url = request.environ.get('pylons.original_request').path
        c.http_error = code = request.environ.get('pylons.original_response').status_int
        m = re.search(r'([^/]+)(/[^/]+/[^/]+/([^/]+))?', orig_url)
        b = m and m.group(1) or None
        if b in ['src', 'thumb']:
            c.pageinfo.title = _(u'some file "%s"')%m.group(3)
        else:
            c.channel = g.boards.get(host=request.environ['HTTP_HOST'])
            c.board = g.boards.boards.get(b, None)
            if c.board and c.board.check_permissions('read', c.admin, c.channel):
                c.pageinfo.setboard(c.board)
            elif b and not re.search(re.compile(u'^[\_\s]*([Дд][OОоo0][Бб6][РPрp]|good|dobr)', re.I), b):
                c.pageinfo.title = u'/%s/'%b
        if code == 404:
            c._404image = g._404images and '/images/404/'+random.choice(list(g._404images)) or u""
            return render('/error/404.mako')
        else:
            c.error_message = _("Error %s")%code
            return render('/error/post.mako')
        
