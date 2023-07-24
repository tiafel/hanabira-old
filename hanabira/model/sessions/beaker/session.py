# -*- coding: utf-8 -*-

import time, re, string, random
from datetime import datetime, timedelta
from beaker.session import Session
from pylons import request, response, app_globals as g, tmpl_context as c

from hanabira.model.referers import Referer
from hanabira.model.admins import Admin, AdminKey
from hanabira.model.restrictions import format_restrictions_reason

from hanabira.lib.useragents import parse_useragent
from hanabira.lib.sites import process_http, URI
from hanabira.lib.utils import ipToInt
from hanabira.lib.visible import VisiblePosts
from hanabira.lib.captcha import Captcha
from hanabira.lib.playlist import PlayList
from hanabira.lib.bookmarks import Bookmarks

import logging
log = logging.getLogger(__name__)

class BeakerSessionManager(object):
    secret = ''
    data_dir = None
    lock_dir = None
    key = 'hanabira'
    timeout = 315360000
    cookie_expires = False
    def __init__(self, config):
        appconf = config['app_conf']
        self.key = appconf.get('beaker.session.key', self.key)
        self.secret = appconf.get('beaker.session.secret', self.secret)
        self.timeout = int(appconf.get('beaker.session.timeout', self.timeout))

        defaultdir = appconf.get('cache_dir') + '/sessions'
        self.data_dir = appconf.get('beaker.session.data_dir', defaultdir)
        self.lock_dir = appconf.get('beaker.session.lock_dir', defaultdir)
        #log.info(self.data_dir)

    def check_cookie(self, env=None):
        pass

    def load(self, env):
        ua = parse_useragent(request)
        sess = None
        if not self.key in request.cookies and ua.is_bot:
            sess = g.bot_session
        if not sess:
            sess = self.load_file(env=env)
        return sess

    def load_by_id(self, id):
        sess = self.load_file(id=id)
        if not sess.is_new:
            sess.init_hanabira()
            return sess
        else:
            return None

    def load_file(self, env=None, id=None):
        if id:
            return BeakerSession({}, use_cookies=False, id=id, 
                              secret=self.secret, 
                              key=self.key,
                              data_dir=self.data_dir,
                              lock_dir=self.lock_dir,
                              cookie_expires=self.cookie_expires,
                              invalidate_corrupt=True,
                              timeout=self.timeout,
                              type=None,
                              log_file=None
                              )
        elif env:
            req = {'cookie_out':None}
            req['cookie'] = env.get('HTTP_COOKIE')
            return BeakerSession(req, use_cookies=True,
                              secret=self.secret, 
                              key=self.key,
                              data_dir=self.data_dir,
                              lock_dir=self.lock_dir,
                              cookie_expires=self.cookie_expires,
                              invalidate_corrupt=True,
                              timeout=self.timeout,
                              type=None,
                              log_file=None
                              )	                           

current_version = 3

def get_prop(prop):
    def get_prop_sub(self):
        return self[prop]
    return get_prop_sub

def set_prop(prop):
    def set_prop_sub(self, val):
        self[prop] = val
    return set_prop_sub
    

class BeakerSession(Session):
    is_bot = False
    def __init__(self, *args, **kw):
        Session.__init__(self, *args, **kw)
        #log.info(self.__dict__)
            
    def update_post_count(self, post, thread, mode='new'):
        if mode == 'delete':
            self.posts_deleted += 1
            if post.op:
                self.threads_deleted += 1
            if not post.invisible and not thread.invisible:
                self.posts_visible -= 1
        elif mode == 'new':
            self.posts_count += 1
            self.posts_chars += len(post.message_raw)
            if post.op:
                self.threads_count += 1
                if thread.invisible:
                    self.threads_invisible += 1
            if not post.invisible and not thread.invisible:
                self.posts_visible += 1
            elif post.invisible:
                self.posts_invisible += 1
            self.last_active = request.now
            self.last_posted = request.now
            self.last_ip = request.ip
        self.save()
    
    def get_tokens(self):
        r = []
        if not self._need_captcha():
            r.append({
                '__class__':'UserToken',
                'token':'no_user_captcha',
                'created_at':None,
                'scope':'0',
                'board_id':None,
                'thread_id':None,
                'tag_id':None,
                'type':'permission',
                'duration':-1,
                'value':None,
                'origin':'auto',
                })
        return r
    
    def get_token(self, token,
                  board=None, board_id=None,
                  thread=None, thread_id=None,
                  tag=None, scope=None):
        r = []
        if not isinstance(token, list):
            token = [token]  
            
        # Normalize scope            
        if thread:
            thread_id = thread.id            
        board_name = None
        if board:
            board_id = board.id
            board_name = board.board            
        
        # Lookup admin tokens
        if self.admin:
            if self.admin.has_permission(token, board_id):
                r.append(0)
                
        now = datetime.now()
        outdated = False
        
        if 'tokens' in self and self['tokens']:
            for td in self.tokens:
                if td[0] in token:
                    if td[2] != -1:
                        if td[3] + td[2] < now:
                            outdated = True
                            continue
                    if td[1][0] == 'global':
                        r.append(td)
                    elif board_name and td[1][0] == 'board' and td[1][1] == board_name:
                        r.append(td)
                    elif thread_id and td[1][0] == 'thread' and td[1][1] == thread_id:
                        r.append(td)
        if outdated:
            self.recheck_tokens()
        return r    
    
    def add_token(self, token, scope, duration, reason_post_id=None, reasons=None, reason_text=None, admin=None):
        if isinstance(duration, int) and duration > 0:
            duration = timedelta(minutes=duration)
        token_data = [token, scope, duration, datetime.now().replace(microsecond=0), {}]
        if reason_post_id:
            token_data[4]['reason_post_id'] = reason_post_id
        if reasons:
            token_data[4]['reasons'] = reasons
        if reason_text:
            if isinstance(reason_text, list):
                reason_text = "; ".join(reason_text)
            token_data[4]['reason_text'] = reason_text
        if admin:
            token_data[4]['admin'] = admin.login
            
        if not 'tokens' in self:
            self['tokens'] = []
            
        self['tokens'].append(token_data)
        
    def remove_token(self, token, scope):
        tokens = []
        for td in self['tokens']:
            if (td[0] != token or (td[1][0] == 'global' and scope[0] != 'global') or
                (td[1][0] != 'global' and (td[1] != scope))):
                tokens.append(td)
        self['tokens'] = tokens
        
    def recheck_tokens(self):
        tokens = []
        now = datetime.now()        
        for td in self['tokens']:
            if td[2] != -1:
                if td[3] + td[2] < now:
                    continue            
            tokens.append(td)
        self['tokens'] = tokens
        
    def add_notice(self, message, level):
        if not 'notices' in self:
            self['notices'] = {}
        mid = str(int(time.time() * 10**5))
        self['notices'][mid] = (message, level)
        return mid
    
    def delete_notice(self, mid):
        if mid in self['notices']:
            del self['notices'][mid]
            
    def get_threads(self, levels=['hidden', 'bookmarked', 'op', 'replied']):
        r = []
        if 'hidden' in levels:
            for board_name, threads in self['hide'].items():
                board = g.boards.get(board=board_name)
                for thread_id in threads:
                    r.append({
                        '__class__':'UserThread',
                        'thread_id': thread_id,
                        'board_id': board.id,
                        'level': 'hidden',
                        'unread': 0,
                        'last_post_id':None,
                        'last_viewed':None,
                        'last_hit':None,
                        })
        if 'bookmarked' in levels:
            for thread_id, board_name in self['bookmarks'].threads.items():
                board = g.boards.get(board=board_name)
                r.append({
                        '__class__':'UserThread',
                        'thread_id': thread_id,
                        'board_id': board.id,
                        'level': 'bookmarked',
                        'unread': 0,
                        'last_post_id':None,
                        'last_viewed':str(self['bookmarks'].visits[thread_id]),
                        'last_hit':None,
                        })                
        return r
        
    def _need_captcha(self):
        if self.get_token('no_captcha'):
            return False
        if not self['enforced_captcha_complexity'] and g.settings.captcha.post_threshold != -1 and g.settings.captcha.post_threshold <= self.posts_visible:
            return False
        else:
            return True        
    
    def set_admin_from_key(self, key):
        ak = AdminKey.query.filter(AdminKey.key == key).first()
        if ak:
            self.admin = ak.admin

    def init_hanabira(self):
        if self.is_new:
            self.init_hanabira_new()
        elif not 'version' in self.accessed_dict:
            self.init_hanabira_v1()
        elif self['version'] == 1:
            self.init_hanabira_v2()
            self.init_hanabira_v3()
        elif self['version'] == 2:
            self.init_hanabira_v3()
        self.admin = self.get('admin', None)

    def persist_hanabira(self):
        if self.is_new:
            self.save()
            response.headers['Set-cookie'] = self.request['cookie_out']

    def init_hanabira_new(self):
        #log.info("New session from {0}".format(request.ip))
        self['version'] = current_version
        self['username'] = {}
        self['stats'] = {}
        self['hide'] = {}
        self['posts'] = {}
        self['hideinfo'] = {}
        self['reply_button'] = 1
        self['rating'] = g.settings.censorship.default
        self['rating_strict'] = g.settings.censorship.strict

        self['redirect'] = 'board'
        self['referer'] = ''
        self['scroll_threads'] = 1
        self['mini'] = 0
        self['enforced_captcha_complexity'] = 0
        self['nopostform'] = 0
        self['reputation_min'] = -5
        self['banners'] = 'different'
        self['password'] = "".join(random.sample(string.ascii_letters+string.digits, 8))
        self.init_language()
        self['bookmarks'] = Bookmarks()
        self['visible_posts'] = VisiblePosts()
        self['captcha'] = Captcha(self)
        self['playlist'] = PlayList()
        
        # v2
        
        self['last_ip'] = request.ip
        self['created_ip'] = request.ip
        self['last_active'] = request.now
        self['last_posted'] = None
        self['posts_count'] = 0
        self['posts_chars'] = 0
        self['posts_deleted'] = 0
        self['posts_visible'] = 0
        self['posts_invisible'] = 0
        self['threads_count'] = 0
        self['threads_deleted'] = 0
        self['threads_invisible'] = 0
        self['is_confirmed'] = 0
        
        self['tokens'] = []
        self['notices'] = {}
        
        self.check_restrictions()


    def init_language(self):
        lang = g.settings.chan.language
        if request.CIS or c.country.lower() in ['ru', 'ua', 'kz', 'by', 'ee', 'lv']:
            lang = 'ru'
        elif c.country.lower() in ['us', 'au', 'uk', 'de', 'fr', 'eu', 'ca', 'gb']:
            lang = 'en'
        elif c.country.lower() in ['jp']:
            lang = 'ja'
        self['language'] = lang	

    def check_restrictions(self):
        effects = g.restrictions.check_session(request)
        if 'premod' in effects:
            self.add_token('premod', ('global', None), -1, reason_text=format_restrictions_reason(effects['premod']))
        # XXX: sync other effects with tokens

    def process_referer(self, referer):
        uri = URI(referer)
        if not uri.proto in ['http', 'https']:
            return None
        process_http(uri, False)
        if uri.domain in g.local_domains:
            return None
        
        orig_ref = uri.text
            
        if uri.domain in g.ignore_referers:
            return None
        if uri.domain in ['google', 'yandex']:
            if not hasattr(uri, 'search_query'):
                return None
            if uri.search_query in g.ignore_queries:
                return None
        if request.environ['QUERY_STRING']:
            target = "%s?%s" % (request.environ['PATH_INFO'], request.environ['QUERY_STRING'])
        else:
            target = request.environ['PATH_INFO']
        Referer(date=datetime.now(), 
                domain=uri.domain, referer=uri.text, target=target,
                ip=ipToInt(request.ip),
                session_id=self.id, session_new=self.is_new).commit()
        
        if self.is_new:
            self['referer'] = orig_ref
            effects = g.restrictions.check_referer(uri, self)
            if 'premod' in effects:
                if 'premod' in effects:
                    self.add_token('premod', ('global', None), -1, reason_text=format_restrictions_reason(effects['premod']))
            self.save()
            
    def init_hanabira_v1(self):
        log.info("Update session to version 1")
        opts = {'username':{}, 'stats':{}, 'referer':'', 'hide':{}, 'posts':{}, 'hideinfo':{}, 'reply_button':1, 'rating':g.settings.censorship.default, 'rating_strict':g.settings.censorship.strict, 'post_count':0, 'deleted_posts':0, 'redirect':'board', 'scroll_threads':1, 'mini':0, 'enforced_captcha_complexity':0, 'nopostform':0, 'reputation_min':-5, 'banners':'different'}

        for o in opts:
            if not o in self:
                self[o] = opts[o]

        if not 'password' in self:
            self['password'] = "".join(random.sample(string.letters+string.digits, 8))

        if not 'language' in self:
            self.init_language()

        if not 'bookmarks' in self:
            if 'signed' in self:
                self['bookmarks'] = Bookmarks(_old=self['signed'])
            else:
                self['bookmarks'] = Bookmarks()

        if not 'visible_posts' in self or self['visible_posts'].__class__ != VisiblePosts:
            self['visible_posts'] = VisiblePosts()

        if not 'captcha' in self:
            self['captcha'] = Captcha(self)


        if not 'playlist' in self:
            if g.settings.player.playlist:
                dpl = [int(x.strip()) for x in g.settings.player.playlist.split(',')]
                dpl = File.query.filter(File.id.in_(dpl)).all()
            else:
                dpl = []
            self['playlist'] = PlayList(default = dpl)


        # Garbage cleanup
        for i in ['invisible_threads', 'my threads', 'invisible_posts', 'boardpage', 'visible_threads', 'captchas', 'signed']:
            if i in self:
                del self[i]

        self['version'] = 1
        self.save()
        
    def init_hanabira_v2(self):
        self['last_ip'] = request.ip
        self['created_ip'] = request.ip
        self['last_active'] = request.now
        self['last_posted'] = None
        self['posts_count'] = self['post_count']
        self['posts_chars'] = 0
        self['posts_visible'] = self['post_count']
        self['posts_deleted'] = self['deleted_posts']
        self['posts_invisible'] = 0
        self['threads_count'] = 0
        self['threads_deleted'] = 0
        self['threads_invisible'] = 0
        self['is_confirmed'] = 0
        
        del self['post_count']
        del self['deleted_posts']
        
        self['version'] = 2
        
        self.save()
        
    def init_hanabira_v3(self):
        self['notices'] = {}
        self['tokens'] = []
        
        del self['invisible']
        del self['inv_reason']
        
        self['version'] = 3
        self.save()
        
        
    # Properties
    created_at = property(get_prop('_creation_time'))

for prop in ['last_active', 'last_posted', 
             'created_ip', 'last_ip',
             'referer', 'password',
             'tokens',
             'posts_count', 'posts_deleted', 'posts_invisible', 'posts_visible',
             'posts_chars',
             'threads_count', 'threads_deleted', 'threads_invisible']:
    setattr(BeakerSession, prop, property(get_prop(prop), set_prop(prop)))

