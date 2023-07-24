# -*- coding: utf-8 -*-

import re, datetime
import pickle
import logging

from sqlalchemy import *
from sqlalchemy.orm import eagerload
from sqlalchemy.ext.declarative import synonym_for

from pylons.i18n import _, ungettext
from pylons import app_globals as g, session

from hanabira.lib.utils import ipToInt
from hanabira.model import meta

log = logging.getLogger(__name__)

restriction_types = ['ip', 'country', 'name', 'password', 'ua', 'file', 'thread', 'word', 'string', 'regexp', 'referer']
effects = ['premod', 'readonly', 'ban', 'captcha', 'nocaptcha', 'whitelist']
class Restriction(meta.Declarative):
    __tablename__ = "restrictions"
    restriction_id = Column(Integer, primary_key=True)
    type           = Column(Enum(*(['none'] + restriction_types)), nullable=False, default='ip')
    value          = Column(Unicode(64), nullable=False)
    date_added     = Column(DateTime, nullable=False, default=datetime.datetime.now)
    duration       = Column(Integer, nullable=False, default=0) # in hours, 0 is infinite
    scope          = Column(Integer, nullable=False, default=0) # 0 for global, otherwise board_id
    expired        = Column(Boolean, default=False)
    effect         = Column(Enum(*effects), nullable=False, default='premod')
    reason         = Column(UnicodeText)
    comment        = Column(UnicodeText)
    
    includes       = Column(Text, nullable=True) # хммм, и чего это такое я хотел?
    __mapper_args__ = {'polymorphic_on': type, 'polymorphic_identity': u'none'}

    @synonym_for('restriction_id')
    @property
    def id(self):
        return self.restriction_id

    def validate(self):
        return bool(self.value)

    @classmethod
    def prepare(cls, restrs):
        rg = {}
        for r in restrs:
            if not r.value in rg:
                rg[r.value] = [r]
        return rg

    @classmethod
    def check(cls, rg, data):
        return []

    def __repr__(self):
        return "<%s(%s => %s)>" % (self.__class__.__name__, self.value.encode('utf-8'), self.effect)
    

class RestrictionIP(Restriction):
    __mapper_args__ = {'polymorphic_identity': u'ip'}
    check_at = ['session']
    
    def validate(self):
        sn = self.value.split('/')
        if len(sn[0].split('.')) == 4:
            return True
        else:
            return False

    def load(self):
        parts = self.value.split('/')
        ip = ipToInt(parts[0])
        self.sn = (len(parts) > 1) and int(parts[1]) or 32
        self.ip = bin(ip)[2:].rjust(32, '0')[:self.sn]
        
    @classmethod
    def prepare(cls, restrs):
        for r in restrs:
            r.load()
        return restrs

    @classmethod
    def check(cls, rg, data):
        if ":" in data.ip:
            return []
        ip = bin(ipToInt(data.ip))[2:].rjust(32, '0')
        effects = []
        for r in rg:
            if ip[:r.sn] == r.ip:
                effects.append(r)
        return effects

class RestrictionCountry(Restriction):
    __mapper_args__ = {'polymorphic_identity': u'country'}
    check_at = ['session']
    @classmethod
    def check(cls, rg, data):
        val = data.country
        if val in rg:
            return rg[val]
        else:
            return []

class RestrictionReferer(Restriction):
    __mapper_args__ = {'polymorphic_identity': u'referer'}
    check_at = ['referer']
    @classmethod
    def check(cls, rg, uri, sess):
        val = uri.domain
        if val in rg:
            return rg[val]
        else:
            return []

class RestrictionPassword(Restriction):
    __mapper_args__ = {'polymorphic_identity': u'password'}
    check_at = ['post']
    @classmethod
    def check(cls, rg, data):
        val = data.password
        if val in rg:
            return rg[val]
        else:
            return []
class RestrictionName(Restriction):
    __mapper_args__ = {'polymorphic_identity': u'name'}
    check_at = ['post']
    @classmethod
    def check(cls, rg, data):
        val = data.name
        if val in rg:
            return rg[val]
        else:
            return []         

class RestrictionUA(Restriction):
    __mapper_args__ = {'polymorphic_identity': u'ua'}
    check_at = ['session']

class RestrictionFile(Restriction):
    __mapper_args__ = {'polymorphic_identity': u'file'}
    check_at = ['post']
    @classmethod
    def check(cls, rg, data):
        for f in data.files:
            val = str(f.file_id)
            if val in rg:
                return rg[val]
            else:
                return []
        return []

class RestrictionThread(Restriction):
    __mapper_args__ = {'polymorphic_identity': u'thread'}
    check_at = ['post']
    @classmethod
    def check(cls, rg, data):
        val = str(data.thread_id)
        if val in rg:
            return rg[val]
        else:
            return []

class RestrictionWord(Restriction):
    __mapper_args__ = {'polymorphic_identity': u'word'}
    check_at = ['post']

class RestrictionString(Restriction):
    """
    >>> r = RestrictionString(value=u'wordfilter', effect='premod')
    >>> r
    <RestrictionString(wordfilter => premod)>
    >>> meta.Session.add(r)
    >>> meta.Session.commit()
    >>> r.restriction_id is not None
    True
    >>> g.restrictions.load()
    """
    __mapper_args__ = {'polymorphic_identity': u'string'}
    check_at = ['post']


    @classmethod
    def prepare(cls, restrs):
        rg = {}
        for r in restrs:
            vl = r.value.lower()
            if not vl in rg:
                rg[vl] = [r]
        return rg

    @classmethod
    def check(cls, rg, data):
        effects = []
        msgraw = data.message_raw.lower()
        name = data.name.lower()
        subj = data.subject.lower()
        for s in rg:
            if s in msgraw or s in name or s in subj:
                effects += rg[s]
        return effects
    

class RestrictionRegexp(Restriction):
    __mapper_args__ = {'polymorphic_identity': u'regexp'}
    check_at = ['post']

    @classmethod
    def prepare(cls, restrs):
        rg = {}
        for r in restrs:
            rg[re.compile(r.value)] = r.effect
        return rg    

def format_restrictions_reason(l):
    res = []
    for r in l:
        if r.comment:
            s = u"{0.type}[{0.value}: {0.comment}]".format(r)
        else:
            s = u"{0.type}[{0.value}]".format(r)
        res.append(s)
    return res

class Restrictions(object):
    classes = {'ip':RestrictionIP, 'country':RestrictionCountry, 'password':RestrictionPassword,
               'ua':RestrictionUA, 'file':RestrictionFile, 'thread':RestrictionThread, 'word':RestrictionWord,
               'string':RestrictionString, 'regexp':RestrictionRegexp, 'name':RestrictionName,
               'referer':RestrictionReferer}
    checks = None
    def __init__(self):
        self.load()

    def load(self):
        self.checks = {'post':{}, 'session':{}, 'referer':{}}
        restrs = Restriction.query.filter(Restriction.expired == False).all()
        for restr in restrs:
            if not restr.__class__ in self.checks[restr.check_at[0]]:
                self.checks[restr.check_at[0]][restr.__class__] = [restr]
            else:
                self.checks[restr.check_at[0]][restr.__class__].append(restr)

        for check_at in self.checks:
            for cls in self.checks[check_at]:
                rg = cls.prepare(self.checks[check_at][cls])
                self.checks[check_at][cls] = rg


    def check_session(self, request):
        effects = {}
        for cls in self.checks['session']:
            ef = cls.check(self.checks['session'][cls], request)
            for r in ef:
                effects.setdefault(r.effect, [])
                effects[r.effect].append(r)
        return effects
            
    def check_post(self, post):
        effects = {}
        for cls in self.checks['post']:
            ef = cls.check(self.checks['post'][cls], post)
            for r in ef:
                effects.setdefault(r.effect, [])
                effects[r.effect].append(r)
        return effects
    
    def check_referer(self, uri, sess):
        effects = {}
        for cls in self.checks['referer']:
            ef = cls.check(self.checks['referer'][cls], uri, sess)
            for r in ef:
                effects.setdefault(r.effect, [])
                effects[r.effect].append(r)
        return effects        
