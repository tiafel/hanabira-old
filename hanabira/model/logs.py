# -*- coding: utf-8 -*-
from sqlalchemy import *
from sqlalchemy.orm import eagerload, relation
from sqlalchemy.ext.declarative import synonym_for
from sqlalchemy.dialects.mysql.base import BIGINT
from hanabira.model import meta
from hanabira.model.admins import Admin
from datetime import datetime
import hashlib, random, string, time
from pylons.i18n import _, ungettext
from pylons import url
import logging
log = logging.getLogger(__name__)

log_types = [u'virtual',
             u'auto_session_ban', u'auto_post_invisible',
             u'user_post_delete', u'op_post_delete', u'user_thread_delete',
             u'mod_post_delete', u'mod_post_invisible', u'mod_thread_delete', u'mod_post_revive',
             u'mod_session_action', u'mod_restriction_action',
             u'mod_login', u'mod_view_post', u'mod_view_session', u'mod_file_edit', u'mod_post_edit']


class BaseEventLog(meta.Declarative):
    __tablename__ = "logs"
    log_id     = Column(Integer, primary_key=True)
    date       = Column(DateTime)
    type       = Column(Enum(*log_types), nullable=False)
    # Used for permission checks and as board_id. 0 for global events and board_id for board events
    scope      = Column(Integer, default=0, index=True)
    session_id = Column(String(64))
    ip         = Column(BIGINT, ForeignKey('ips.ip'), nullable=True, index=True)

    # Should be subclassed, but not sure how to do it
    admin_id   = Column(Integer, ForeignKey('admins.admin_id'), index=True)
    post_id    = Column(Integer)
    restriction_id  = Column(Integer, ForeignKey('restrictions.restriction_id'))
    target_admin_id = Column(Integer)
    target_session_id = Column(String(64))
    file_id    = Column(Integer, ForeignKey('files.file_id'), index=True)
    reason     = Column(UnicodeText)
    action          = Column(UnicodeText)
    __mapper_args__ = {'polymorphic_on': type, 'polymorphic_identity': u'virtual'}
    admin      = relation(Admin)

    @synonym_for('log_id')
    @property
    def id(self):
        return self.log_id

    def __init__(self, ip, session_id, commit=False, add=True, **kw):
        self.ip = ip
        self.session_id = session_id
        self.date = datetime.now()
        if add:
            meta.Session.add(self)
            if commit:
                meta.Session.commit()

    def get_message(self):
        return u""

    def export(self):
        return {'date':str(self.date), 'event':self.get_message()}

class AutoSessionBan(BaseEventLog):
    __mapper_args__ = {'polymorphic_identity': u'auto_session_ban'}
    def __init__(self, ip, session, **kw):
        BaseEventLog.__init__(self, ip, session.id, **kw)
        self.scope = 0
        meta.Session.add(self)
        meta.Session.commit()

    def get_message(self):
        return u"Session was auto-banned."

class AutoPostInvisible(BaseEventLog):
    __mapper_args__ = {'polymorphic_identity': u'auto_post_invisible'}
    def __init__(self, ip, session_id, post, restriction_id, reason, **kw):
        self.post_id = post.id
        self.scope   = post.thread.board_id
        self.restriction_id = restriction_id
        self.reason = reason
        BaseEventLog.__init__(self, ip, session_id, **kw)

    def get_message(self):
        return u"Post {0.post_id} was auto-invised due to {0.reason}.".format(self)

class UserPostDeleteLog(BaseEventLog):
    __mapper_args__ = {'polymorphic_identity': u'user_post_delete'}
    def __init__(self, ip, session_id, post, **kw):
        self.post_id = post.id
        self.scope   = post.thread.board_id
        BaseEventLog.__init__(self, ip, session_id, **kw)

    def get_message(self):
        return u"User deleted his post {0.post_id}".format(self)

class OPPostDeleteLog(BaseEventLog):
    __mapper_args__ = {'polymorphic_identity': u'op_post_delete'}
    def __init__(self, ip, session_id, post, **kw):
        self.post_id = post.id
        self.scope   = post.thread.board_id
        BaseEventLog.__init__(self, ip, session_id, **kw)

    def get_message(self):
        return u"OP deleted post {0.post_id}".format(self)

class UserThreadDeleteLog(BaseEventLog):
    __mapper_args__ = {'polymorphic_identity': u'user_thread_delete'}
    def __init__(self, ip, session_id, thread, **kw):
        self.post_id = thread.op_id
        self.scope   = thread.board_id
        BaseEventLog.__init__(self, ip, session_id, **kw)

    def get_message(self):
        return u"User deleted his thread {0.post_id}".format(self)

class ModPostDeleteLog(BaseEventLog):
    __mapper_args__ = {'polymorphic_identity': u'mod_post_delete'}
    def __init__(self, ip, session_id, admin, post, reason, **kw):
        self.admin_id = admin.id
        self.post_id  = post.id
        self.reason   = reason
        self.scope    = post.thread.board_id
        BaseEventLog.__init__(self, ip, session_id, **kw)

    def get_message(self):
        return u"Admin {0.admin.login} deleted post {0.post_id} for {0.reason}".format(self)

class ModThreadDeleteLog(BaseEventLog):
    __mapper_args__ = {'polymorphic_identity': u'mod_thread_delete'}
    def __init__(self, ip, session_id, admin, thread, reason, **kw):
        self.admin_id = admin.id
        self.post_id  = thread.op_id
        self.reason   = reason
        self.scope    = thread.board_id
        BaseEventLog.__init__(self, ip, session_id, **kw)

    def get_message(self):
        return u"Admin {0.admin.login} deleted thread {0.post_id} for {0.reason}".format(self)

class ModRevivePost(BaseEventLog):
    __mapper_args__ = {'polymorphic_identity': u'mod_post_revive'}
    def __init__(self, ip, session_id, admin, post, **kw):
        self.admin_id = admin.id
        self.post_id  = post.id
        self.scope    = post._thread.board_id
        BaseEventLog.__init__(self, ip, session_id, **kw)

    def get_message(self):
        return u"Admin {0.admin.login} revived post {0.post_id}".format(self)    

class ModPostInvisibleLog(BaseEventLog):
    __mapper_args__ = {'polymorphic_identity': u'mod_post_invisible'}
    def __init__(self, ip, session_id, admin, post, action, **kw):
        self.admin_id = admin.id
        self.post_id  = post.id
        self.action   = action
        self.scope    = post.thread.board_id
        BaseEventLog.__init__(self, ip, session_id, **kw)

    def get_message(self):
        return u"Admin {0.admin.login} made post {0.post_id} {0.action}".format(self)

class ModSessionActionLog(BaseEventLog):
    __mapper_args__ = {'polymorphic_identity': u'mod_session_action'}

    def __init__(self, ip, session_id, admin, target_session_id, action, **kw):
        self.admin_id = admin.id
        self.target_session_id = target_session_id
        self.action = action
        self.scope  = 0
        BaseEventLog.__init__(self, ip, session_id, **kw)

    def get_message(self):
        return u"Admin {0.admin.login} {0.action} <a href='{1}'>session</a>.".format(self, url('session', session_id=self.target_session_id))

class ModRestrictionActionLog(BaseEventLog):
    __mapper_args__ = {'polymorphic_identity': u'mod_restriction_action'}

    def __init__(self, ip, session_id, admin, restriction, action, **kw):
        self.admin_id = admin.id
        self.restriction_id = restriction.id
        self.scope  = restriction.scope
        self.action = action
        BaseEventLog.__init__(self, ip, session_id, **kw)

    def get_message(self):
        return u"Admin {0.admin.login} {0.action} restriction {0.restriction_id}".format(self)

class ModLogin(BaseEventLog):
    __mapper_args__ = {'polymorphic_identity': u'mod_login'}
    def __init__(self, ip, session_id, admin, **kw):
        self.admin_id = admin.id
        BaseEventLog.__init__(self, ip, session_id, **kw)

    def get_message(self):
        return u"Mod {0.admin.login} logged in".format(self)
    
class ModViewPost(BaseEventLog):
    __mapper_args__ = {'polymorphic_identity': u'mod_view_post'}
    def __init__(self, ip, session_id, admin, post, **kw):
        self.admin_id = admin.id
        self.post_id  = post.id
        self.scope    = post._thread.board_id
        BaseEventLog.__init__(self, ip, session_id, **kw)

    def get_message(self):
        return u"Admin {0.admin.login} viewed post {0.post_id}".format(self)
    
class ModEditPost(BaseEventLog):
    __mapper_args__ = {'polymorphic_identity': u'mod_post_edit'}
    def __init__(self, ip, session_id, admin, post, **kw):
        self.admin_id = admin.id
        self.post_id  = post.id
        self.scope    = post.thread and post.thread.board_id or 0
        BaseEventLog.__init__(self, ip, session_id, **kw)

    def get_message(self):
        return u"Admin {0.admin.login} edited post {0.post_id}".format(self)    
    
class ModViewSession(BaseEventLog):
    __mapper_args__ = {'polymorphic_identity': u'mod_view_session'}

    def __init__(self, ip, session_id, admin, target_session_id, **kw):
        self.admin_id = admin.id
        self.target_session_id = target_session_id
        self.scope  = 0
        BaseEventLog.__init__(self, ip, session_id, **kw)

    def get_message(self):
        return u"Admin {0.admin.login} viewed <a href='{1}'>session</a>.".format(self, url('session', session_id=self.target_session_id))

class ModEditFile(BaseEventLog):
    __mapper_args__ = {'polymorphic_identity': u'mod_file_edit'}

    def __init__(self, ip, session_id, admin, file_id, **kw):
        self.admin_id = admin.id
        self.file_id = file_id
        self.scope  = 0
        BaseEventLog.__init__(self, ip, session_id, **kw)

    def get_message(self):
        return u"Admin {0.admin.login} edited <a href='{1}'>file</a>.".format(self, url('files_id', file_id=self.file_id))

class IP(meta.Declarative):
    __tablename__ = "ips"
    ip         = Column(BIGINT, primary_key=True)
    country    = Column(String(32))
    city       = Column(String(32))
    provider   = Column(String(32))
    visits     = Column(Integer)
    posts      = Column(Integer)
    last_visit = Column(DateTime)
    

__all__ = ['ModEditFile', 'ModEditPost', 'ModLogin', 
           'ModPostDeleteLog', 'ModPostInvisibleLog', 'ModRestrictionActionLog', 
           'ModRevivePost', 'ModSessionActionLog', 'ModThreadDeleteLog', 'ModViewPost',
           'ModViewSession',
           'UserPostDeleteLog', 'UserThreadDeleteLog', 'OPPostDeleteLog',
           'AutoSessionBan', 'AutoPostInvisible',
           'IP',
           'BaseEventLog']