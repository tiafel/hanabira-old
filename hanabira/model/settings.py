# -*- coding: utf-8 -*-
from pylons.i18n import _, ungettext, N_, lazy_gettext
from sqlalchemy import *
from pylons import config
import pkg_resources
from hanabira.model import meta
import datetime, re

import logging
log = logging.getLogger(__name__)

class Setting(meta.Declarative):
    __tablename__ = "settings"
    id    = Column(Integer, primary_key=True)
    name  = Column(String(64), nullable=False)
    type  = Column(Unicode(8), nullable=False)
    value = Column(UnicodeText, nullable=False)
    __mapper_args__ = {'polymorphic_on': type, 'polymorphic_identity': u'None'}
    def __init__(self, name, value):
        self.name = name
        self.set(value)
        meta.Session.commit()


    def load(self):
        self.value_cached = self.getvalue()

    def set(self, value):
        self.value = unicode(value)
        
    def __repr__(self):
        return self.value

    def __str__(self):
        return str(self.__repr__())

    def getvalue(self):
        return self.value

    def render(self):
        return '<input type="text" name="%s" value="%s">' % (self.name, self.value)

class BooleanSetting(Setting):
    __mapper_args__ = {'polymorphic_identity': u'Boolean'}
    def set(self, value):
        if not value:
            self.value = u"False"
        else:
            self.value = unicode(value)

    def bool(self):
        if self.value == u"False" or bool(self.value) == False:
            return False
        else:
            return True
        
    def getvalue(self):
        return self.bool()
    
    def __repr__(self):
        return self.bool()
    
    def __nonzero__(self):
        return self.bool()

    def render(self):
        return '<input type="checkbox" name="%s" %s>' % (self.name, self.getvalue() and "checked")
    
class StringSetting(Setting):
    __mapper_args__ = {'polymorphic_identity': u'String'}

    def getvalue(self):
        return self.value
    
    def __repr__(self):
        return unicode(self.value)

    def __str__(self):
        return self.value
    def __unicode__(self):
        return self.value

class IntegerSetting(Setting):
    __mapper_args__ = {'polymorphic_identity': u'Integer'}
    def __repr__(self):
        return int(self.value)

    def getvalue(self):
        return int(self.value)

class ListSetting(Setting):
    __mapper_args__ = {'polymorphic_identity': u'List'}
    def __repr__(self):
        return self.value

class ConfSetting(object):
    def __init__(self, name, value):
        self.name = name
        self.value = value
    def __repr__(self):
        return self.value
    def __str__(self):
        return str(self.__repr__())

class Bag(object):
    def __getattribute__(self, attr, **kwords):
        r = object.__getattribute__(self, attr, **kwords)
        if isinstance(r, Setting):
            return r.value_cached
        else:
            return r

class Settings(object):
    """
    Collection of setting instances
    self.reference contains list of all avaiable settings with
    types and default values
    Avaiable types are:
       Boolean
       String
       Integer
       List
       Conf - value is loaded from config file, and cannot be edited from web
    """
    reference = {
        "chan.title":          (u'String',  u'Hanabira',            lazy_gettext("Board title")),
        "chan.logo":           (u'String',  u'',                    lazy_gettext("Chan logo")),
        "chan.keywords":       (u'String',  u'hanabira board chan', lazy_gettext("Chan keywords")),
        "chan.description":    (u'String',  u'some imageboard',     lazy_gettext("Chan meta description")),
        "chan.language":       (u'String',  u'en',                  lazy_gettext("Chan language")),
        "chan.domain":         (u'String',  u'hanabira.ru',         lazy_gettext("Chan domain")),
        "chan.local_domains":  (u'Conf',  u'hanabira.ru',           lazy_gettext("Chan local domains")),
        "chan.debug":          (u'Boolean', False,                  lazy_gettext("Debug mode")),
        "chan.timeformat":     (u'String',  u'%d %B %Y (%a) %H:%M', lazy_gettext("Time format string (strftime)")),
        "chan.mini_timeformat":     (u'String',  u'%d %b %Y %H:%M', lazy_gettext("Time format string (strftime)")),
        "player.enabled":      (u'Boolean', True,                   lazy_gettext("Music player")),
        "player.playlist":     (u'String',  u'',                    lazy_gettext("Default playlist")),
        "featured.news":       (u'String',  u'',                    lazy_gettext("News board")),
        "path.temp":           (u'Conf',    u'/tmp/',               lazy_gettext("Temporary files")),
        "path.static":         (u'Conf',    u'',                    lazy_gettext("Path to static files")),
        "path.static_web":     (u'Conf',    u'/',                   lazy_gettext("Static access from web")),
        "security.hash.salt":  (u'Conf',    u'youshouldchangethis', lazy_gettext("Hashes salt")),
        "security.link.masker":(u'String',  u'http://anonym.to/?',  lazy_gettext("Mask links with this anonymizer")),
        "censorship.enabled":  (u'Boolean', True,                   lazy_gettext("Files censorship ratings")),
        "censorship.default":  (u'String',  u'r-15',                lazy_gettext("Default censorship rating")),
        "censorship.strict":   (u'Boolean', True,                   lazy_gettext("Default censorship strictness")),
        "captcha.default_complexity": (u"Integer", 20,              lazy_gettext("Default captcha complexity")),
        "captcha.optional_complexity": (u"Integer", 40,             lazy_gettext("Complexity for optional captchas")),
        "captcha.post_threshold":(u'Integer', 10,                   lazy_gettext("Amount of posts to turn off captcha")),
        "captcha.new_thread_penalty":(u'Integer', 100,              lazy_gettext("Penalty for going over new threads limit")),
        "captcha.reply_penalty":(u'Integer', 50,                    lazy_gettext("Penalty for going over consecutive replies limit")),
        "captcha.bump_penalty":(u'Integer', 100,                    lazy_gettext("Penalty for bumping old thread")),        
        "post.lines_limit":    (u'Integer', 15,                     lazy_gettext("Show only so much lines")),
        "post.chars_limit":    (u'Integer', 2000,                   lazy_gettext("Show only so much characters")),
        "post.filename_limit": (u'Integer', 20,                     lazy_gettext("Filename length limit")),
        "file.sound.ov_file":  (u'String',  u'images/sound_over.png',  lazy_gettext("Sound thumb mark")),
        "file.text.bg_file":   (u'String',  u'images/text_bg.png',  lazy_gettext("Text thumb background")),
        "file.text.ov_file":   (u'String',  u'images/text_ov.png',  lazy_gettext("Text thumb cover")),
        "file.text.x_offset":  (u'Integer', 10,                     lazy_gettext("Text thumb overlay x offset")),
        "file.text.y_offset":  (u'Integer', 3,                      lazy_gettext("Text thumb overlay y offset")),
        "file.text.width":     (u'Integer', 186,                    lazy_gettext("Text thumb overlay width")),
        "file.text.height":    (u'Integer', 187,                    lazy_gettext("Text thumb overlay height")),
        "sphinx.enabled":      (u'Boolean', False,                  lazy_gettext("SphinxSearch enabled")),
        "sphinx.host":         (u'String',  u'127.0.0.1',           lazy_gettext("SphinxSearch host")),
        "sphinx.port":         (u'Integer', 3355,                   lazy_gettext("SphinxSearch port")),
        "sphinx.index_posts":  (u'String',  u'hanabira_posts_idx',  lazy_gettext("SphinxSearch index for posts, by message_raw and subject")),
        "sphinx.index_files":  (u'String',  u'hanabira_files_idx',  lazy_gettext("SphinxSearch index for files, by filename and metainfo")),
        "sphinx.maximum":      (u'Integer', 1000,                   lazy_gettext("SphinxSearch maximum records per search")),
        "sphinx.per_page":     (u'Integer', 20,                     lazy_gettext("SphinxSearch threads per page")),
        "trace.enabled":       (u'Conf',  u'',                      lazy_gettext("Tracing")),
        "trace.time_limit":       (u'Conf',  u'',                      lazy_gettext("Tracing")),
        "trace.time_show_all":       (u'Conf',  u'',                      lazy_gettext("Tracing")),
        "trace.request_show_all":       (u'Conf',  u'',                      lazy_gettext("Tracing")),
        "cluster.slave_nodes":(u'Conf', u'', lazy_gettext("List of application slave nodes")),
        }
    
    class_map = {
        "String": StringSetting,
        "Integer": IntegerSetting,
        "List": ListSetting,
        "Boolean": BooleanSetting,
        "Conf": ConfSetting
        }
    _all = None
    config = None
    def __init__(self, config):
        self.config = config
        self.load()

    def load(self):
        log.info("Initializing Settings()")
        self._all = {}
        for setting_fullname in self.reference:
            setting_type, setting_default, setting_description = self.reference[setting_fullname]
            setting_path = setting_fullname.split('.')
            setting_name = setting_path.pop()
            setting_parent = self
            for node in setting_path:
                if not hasattr(setting_parent, node):
                    setting_parent.__setattr__(node, Bag())
                setting_parent = setting_parent.__getattribute__(node)
            if setting_type != "Conf":
                setting = Setting.query.filter(Setting.name == setting_fullname).first()
                if not setting is None:
                    setting.load()
            else:
                setting = ConfSetting(setting_fullname, self.config.get(setting_fullname, setting_default))
            if setting is None:
                setting = self.class_map[setting_type](setting_fullname, setting_default)
                meta.Session.add(setting)
                setting.load()
            setting.__setattr__('description', setting_description)
            setting_parent.__setattr__(setting_name, setting)
            self.__setattr__(setting_fullname, setting)
            self._all[setting_fullname] = setting
            log.info("... %s == %s" % (setting_fullname, setting))
        meta.Session.commit()
        self.dist = pkg_resources.get_distribution("hanabira")
        log.info("dist.version == %s" % self.dist.version)
