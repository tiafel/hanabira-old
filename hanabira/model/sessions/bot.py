# -*- coding: utf-8 -*-

from hanabira.lib.useragents import parse_useragent
from hanabira.lib.sites import process_http, URI
from hanabira.lib.utils import ipToInt
from hanabira.lib.visible import VisiblePosts
from hanabira.lib.captcha import Captcha
from hanabira.lib.playlist import PlayList
from hanabira.lib.bookmarks import Bookmarks

class BotSession(object):
    is_new = False
    is_bot = True
    id = 'bot_session'

    def __init__(self, g):
        self.username = {}
        self.stats = {}
        self.hide = {}
        self.posts = {}
        self.hideinfo = {}
        self.reply_button = 1
        self.redirect = 'board'
        self.scroll_threads = 1
        self.mini = 0
        self.enforced_captcha_complexity = 0
        self.nopostform = 0
        self.reputation_min = -5
        self.banners = 'different'
        self.referer = ''
        self.password = "bot_session"
        self.language = 'ru'
        self.inv_reason = ['Bot']
        self.invisible = True
        self.rating = g.settings.censorship.default
        self.rating_strict = g.settings.censorship.strict    
        self.bookmarks = Bookmarks()
        self.visible_posts = VisiblePosts()
        self.captcha = Captcha(self)
        self.playlist = PlayList()
        self.admin = None
        self.last_ip = None
        self.created_ip = None
        self.last_active = None
        self.last_posted = None
        self.posts_count = 0
        self.posts_chars = 0
        self.posts_deleted = 0
        self.posts_invisible = 0
        self.posts_visible = 0
        self.threads_count = 0
        self.threads_deleted = 0
        self.threads_invisible = 0
        self.is_confirmed = 0        

    def init_hanabira(self):
        pass

    def persist_hanabira(self):
        pass

    def get(self, *arg, **kw):
        return self.__dict__.get(*arg, **kw)

    def __getitem__(self, *arg, **kw):
        try:
            return self.__dict__.__getitem__(*arg, **kw)
        except KeyError:
            return None

    def save(self):
        pass

    def process_referer(self, ref):
        pass
    
    def get_token(self, token,
                  board=None, board_id=None,
                  thread=None, thread_id=None,
                  tag=None):
        return []   
    def get_tokens(self):
        return []
    def get_threads(self):
        return []
    
    def set_admin_from_key(self, key):
        pass
