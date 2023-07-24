# -*- coding: utf-8 -*-
"""The base Controller API
Provides the BaseController class for subclassing, and other objects
utilized by Controllers.
"""

from pylons import tmpl_context as c, cache, config, app_globals as g, request, response, session, url
from pylons.controllers import WSGIController
from pylons.controllers.util import abort, etag_cache, redirect
from pylons.i18n import _, ungettext, N_, get_lang, set_lang

from datetime import datetime, timedelta
import simplejson as json
import time, re, string, random
import hashlib
import traceback

from sqlalchemy.orm import eagerload, lazyload, relation, contains_eager
from sqlalchemy.sql import and_, or_, not_, func, union

import hanabira.lib.helpers as h
from hanabira.lib.utils import ipToInt, parse_url, safe_int
import hanabira.model as model
from hanabira.model import meta
from hanabira.model.files import File
from hanabira.model.admins import AdminKey
from hanabira.lib.trace import trace_log, trace_time, render
from hanabira.lib.export import api_ok
from hanabira.lib.permissions import PermissionException

import logging

log = logging.getLogger(__name__)

cis_countries = ['RU', 'BY', 'KZ', 'UA', 'EE', 'LV']

class PageInfo(object):
    page = None
    chan_title = ''
    title = ''
    long_title = ''
    description = ''
    subtitle = ''
    keywords = ''
    meta_description = ''
    language = ''
    
    upper_banner = ''
    lower_banner = ''
    
    @property
    def title_logo(self):
        return self.long_title or self.title

    def __init__(self, settings):
        self.keywords = settings.chan.keywords
        self.meta_description = settings.chan.description
        self.language = settings.chan.language
        self.chan_title = c.channel.title
        #self.upper_banner = c.channel.upper_banner
        if c.channel.lower_banner:
            self.lower_banner = c.channel.lower_banner

    def setboard(self, board):
        if board.keywords:
            self.keywords = board.keywords
        if board.meta_description:
            self.meta_description = board.meta_description
        elif board.description:
            self.meta_description = board.description
        else:
            self.meta_description = board.long_title or board.title
        self.title = board.title
        self.long_title = board.long_title
        self.description = board.description

    def setthread(self, thread):
        if thread.deleted:
            self.description = _("This thread is deleted.")
        self.subtitle = thread.title
        self.meta_description = None
        self.keywords = None
        
    def setpage(self, page=None):
        if page is None:
            if c.referer:
                self.page = int(parse_url(c.referer).get('page') or 0)
        else:
            self.page = safe_int(page)
        
    def set(self, board=None, thread=None, page=None):
        if board:
            self.setboard(board)
        if thread:
            self.setthread(thread)
        if self.page is None:
            self.setpage(page)

def handle_last_modified(lastmodified, lastmodified2=None):
    #log.info(lastmodified)
    #log.info(lastmodified2)
    if lastmodified2 and lastmodified2 > lastmodified:
        lastmodified = lastmodified2
    response.last_modified = lastmodified
    if request.if_modified_since:
        rims = list(request.if_modified_since.utctimetuple())[0:6]
        rims = datetime(*rims)
        # XXX: fix summer-time difference!
        #log.info(("last_mod", rims, lastmodified))
        #rims = rims + timedelta(hours=1)
        if rims == lastmodified:
            return abort(304)

def handle_etag(etag, time=None):
    if type(etag) is list:
        etag = '-'.join(etag)
    elif not isinstance(etag, str):
        etag = str(etag)
    if time:
        etag = etag + '-' + str(time)
    response.etag = etag
    if request.if_none_match and request.if_none_match.etags:
        for req_etag in request.if_none_match.etags:
            if req_etag == etag:
                return abort(304)
    
class BaseController(WSGIController):
    def __call__(self, environ, start_response):
        
        request.country = request.headers.get("X-Country", "NA")
        
        if not environ['REQUEST_METHOD'] in ['GET', 'POST']:
            start_response('405 Method Not Allowed',
                           [('Content-Type','text/html')])
            return ['Only GET and POST methods are supported.']
        
        if ('X-SERV-PROTO' in request.headers and
            request.headers.get('X-SERV-PROTO') != "HTTP/1.1" and
            request.country not in cis_countries):
            pass
            #start_response('405 Method Not Allowed',
            #               [('Content-Type','text/html')])
            #return ['Request denied because either proxy or bot detected.']
        """    
        if request.headers.get('HTTP_REFERER', '').lower() == 'http://dva-ch.ru/':
            log.info("Drop DDPS {0}".format(request.headers.get("X-Real-IP", request.environ.get("REMOTE_ADDR", "127.0.0.1"))))
            start_response('405 Method Not Allowed',
            [('Content-Type','text/html')])
            return ['Bots are not allowed.']
        """
        if 'DobroReader/3.3.13' in request.headers.get('USER_AGENT', ''):
            log.info('DR 403 {0}'.format(request.headers.get("X-Real-IP", request.environ.get("REMOTE_ADDR", "127.0.0.1"))))
            start_response('403 Forbidden',
            [('Content-Type','text/html')])
            return ['This version of Dobroreader contains malware harmful to both your device and Dobrochan.ru, please downgrade or uninstall it immediately. More details at >>/d/40584']
        
        
        trace_time('call')
        
        session._push_object(g.sessions.load(env=environ))
        # TODO: Make a setting for this
        if (
            False and
            (session.is_new or session.posts_visible < 1) and
            not 'key' in  request.GET
            #and (request.country not in cis_countries or session.is_new)
            #and request.country !='RU'
            and request.country not in ('RU', 'UA')
            ):
            log.info("503 for {0} [{1}], {2}".format(request.headers.get("X-Real-IP", request.environ.get("REMOTE_ADDR", "127.0.0.1")), request.country, session.id))
            start_response('503 Service Unavailable',
            [('Content-Type','text/html')])
            return ['Due to overload, access is limited to site members only.']
        
        if session.is_bot:
            if request.headers.get("X-Real-IP", request.environ.get("REMOTE_ADDR", "127.0.0.1")) != "127.0.0.1":
                start_response('503 Service Unavailable', [('Content-Type','text/html')])
                return ['Search bots disabled for a while.']
    
        try:
            res = WSGIController.__call__(self, environ, start_response)
            return res
        except Exception as e:
            #log = logging.getLogger('hanabira.httpserver')
            dt = str(datetime.now())
            ip = request.headers.get("X-Real-IP", request.environ.get("REMOTE_ADDR", "127.0.0.1"))
            ureq_id = hashlib.sha256((dt + ip).encode('utf-8')).hexdigest()
            log.critical("Exception happened, RefID:{0}; URL:{1}; IP:{2}; SessionID:{3}".format(
                ureq_id, request.environ['PATH_INFO'], ip, session.id))
            log.critical(traceback.format_exc())            
            start_response('503 Service Unavailable',
                           [('Content-Type','text/html')])
            return ['Some unexpected problem happened during processing of your request. All details were logged, problem unique reference ID: {0}'.format(ureq_id)]
        finally:
            if str(g.settings.trace.enabled) == 'true':
                c.tracer.trace('call')
                c.tracer.print_times()            
                
            session._pop_object()
            meta.Session.remove()

    def _get_admin(self, key, ctx):
        if ctx.admin:
            return ctx.admin
        elif key:
            keyadm = AdminKey.query.filter(AdminKey.key == key).first()
            if keyadm:
                return keyadm.admin
        return None
        
    def init_request(self):
        trace_time('before')
        c.ip = request.ip = ip = request.headers.get("X-Real-IP", request.environ.get("REMOTE_ADDR", "127.0.0.1"))
        proxy_ip = request.headers.get("X-Forwarded-For", "").split(',')[0].strip()
        c.country = request.country
        request.CIS = request.headers.get('X-CIS', False)
        request.SSL = request.headers.get('X-SSL', False)
        request.now = datetime.now()
        if request.SSL:
            request.environ['wsgi.url_scheme'] = 'https'
        if proxy_ip and proxy_ip != ip:
            # Check wheter we allowed this proxy
            #log.info("Proxy request %s -> %s" % (ip, proxy_ip))
            effects = g.restrictions.check_session(request)
            if 'whitelist' in effects:
                c.ip = request.ip = proxy_ip

        if (str(g.settings.trace.enabled) == 'true' and
            str(g.settings.trace.request_show_all) == 'true'):
            trace_log.warn(c.tracer.header)

    def __before__(self, **kw):
        self.init_request()
        c.channel  = g.boards.get(host=request.environ['HTTP_HOST'])
        c.pageinfo = PageInfo(g.settings)
        # Nose and webtest do not provide ip
        session.init_hanabira()
        
        if (
            False and
            session.posts_visible < 1 and not session.get_token('premod')
            ):
            session.add_token('premod', ('global', None), -1, reason_text="New session, temporary")
            log.info("Banned new session, {0} [{1}], {2}".format(request.headers.get("X-Real-IP", request.environ.get("REMOTE_ADDR", "127.0.0.1")), request.country, session.id))
        
        session.persist_hanabira()
        c.admin = session.get('admin', None)
        c.session = session
        c.viewer_session = session
        for i in ['username', 'password', 'redirect', 'rating', 'rating_strict', 'reply_button', 'language', 'playlist', 'hideinfo', 'scroll_threads', 'mini', 'nopostform', 'reputation_min', 'banners']:
            c.__setattr__(i, session[i])
        
        set_lang(c.language)

        c.session_id = session.id

        # Handle referers
        referer = request.headers.get('Referer', '')
        if referer:
            session.process_referer(referer)
            
        trace_time('before')

    def _return(self, result):
        response.headers['Content-Type'] = 'application/json'
        return json.dumps(result)

    def _result(self, result):
        return self._return({'status':'ok', 'result':result})

    def _error(self, error):
        return self._return({'status':'error', 'error':error})

# Include the '_' function in the public names
__all__ = [__name for __name in list(locals().keys()) if not __name.startswith('_') \
           or __name == '_']
