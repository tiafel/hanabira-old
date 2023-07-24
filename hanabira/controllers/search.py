# -*- coding: utf-8 -*-
import logging
import time
import os

from hanabira.lib.utils import *
from hanabira.lib.base import *

log = logging.getLogger(__name__)

class SearchController(BaseController):
    def __before__(self):
        BaseController.__before__(self)
        c.pageinfo.title = _("Search")
        c.errors = []
        c.query = u""
        c.admin = session.get('admin', None)
    
    def search(self, search_id, page, ext):
        if page == 'index':
            page = 0
        page = int(page)
        c.pageinfo.page = page
        search_id = int(search_id)
        log.info("search(%s, %s, %s)" % (search_id, page, ext))
        search = g.searches.get(search_id)
        log.info(search)
        if search:
            c.search = search
            c.pages = search.pages
            c.threads = search.get_threads(page=page, admin=c.admin, visible_posts=session['visible_posts'])
            return render('/search/result.mako')
        else:
            c.errors = [_("No such search query found")]
            return render('/search/form.mako')

    def search_new(self, ext):
        c.query = query = unicode(request.POST.get('query', '')).strip()
        log.info("search_new(%s, %s)" % (query, ext))
        if not query:
            redirect(url('search_form', ext='xhtml'))
        if not g.settings.sphinx.enabled:
            log.info("Sphinx is disabled")
            c.errors = [_("Sphinx is disabled")]
            return render('/search/form.mako')
        board_id = int(request.POST.get('board_id', '0'))
        query = re.sub(u'(\S)-(\S)', r'\1 \2', query)
        search = g.searches.check(query)
        if not search:
            search = g.searches.new(query, board_id=board_id)
        if search and search.count:
            redirect(url('search', search_id=search.id, ext=ext))
        else:
            c.errors = [_("No records found")]
            return render('/search/form.mako')

    def search_form(self, ext):
        log.info("search_form(%s)" % (ext))
        return render('/search/form.mako')
