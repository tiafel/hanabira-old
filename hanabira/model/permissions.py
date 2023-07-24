# -*- coding: utf-8 -*-
from sqlalchemy import *
from sqlalchemy.orm import eagerload
from sqlalchemy.ext.declarative import synonym_for
from hanabira.model import meta
from pylons.i18n import _, ungettext, N_
import pickle
import logging
log = logging.getLogger(__name__)

class Permission(meta.Declarative):
    __tablename__ = "permissions"
    permission_id = Column(Integer, primary_key=True)
    name          = Column(Unicode(16), nullable=False, unique=True)
    type          = Column(Unicode(8), nullable=False)
    includes      = Column(Text, nullable=True)
    __mapper_args__ = {'polymorphic_on': type, 'polymorphic_identity': u'simple'}
    
    @synonym_for('permission_id')
    @property
    def id(self):
        return self.permission_id
    
    def __init__(self, name=None):
        if name:
            self.name = name
            meta.Session.add(self)
            meta.Session.commit()
    
    def expand(self):
        return [self.name]

    @property
    def id(self):
        return self.permission_id

    @classmethod
    def get(cls, name):
        return cls.query.filter(cls.name == name).first()

    def __repr__(self):
        return "<Permission(%s)>" % self.name

class CompoundPermission(Permission):
    __mapper_args__ = {'polymorphic_identity': u'compound'}
    def __init__(self, name=None, includes=None, includes_names=None):
        if includes_names:
            includes = self.get_includes(includes_names)
        meta.Session.add(self)
        if name or includes:
            self.update(name, includes)

    @classmethod
    def get_includes(cls, includes_names):
        result = []
        for name in includes_names:
            result.append(Permission.get(name))
        return result
        
    def update(self, name=None, permissions=None):
        if name:
            self.name = name
        if permissions:
            self.update_permissions(permissions)
        meta.Session.commit()

    def update_permissions(self, permissions):
        includes = []
        for permission in permissions:
            includes.append(permission.id)
        self.includes = pickle.dumps(includes)

    @property
    def permissions(self):
        ids = pickle.loads(self.includes.encode('utf-8'))
        result = []
        for pid in ids:
            result.append(Permission.query.filter(Permission.permission_id == pid).first())
        return result
    
    def expand(self):
        result = []
        for permission in self.permissions:
            result += permission.expand()
        return result

    def __repr__(self):
        return "<CompoundPermission(%s) %s>" % (self.name, map(lambda x:x.name, self.permissions))

class Permissions(object):
    """
    Collection of Permission instances
    """
    defaults_simple = [
        u'read', u'new_thread', u'new_reply', u'reputation',
        u'delete_posts', u'delete_threads', u'edit_posts', u'view_ip', u'view_log', u'sessions', u'see_invisible', u'view_deleted',
        u'manage_archive', u'manage_threads', u'featured',
        u'view_admins', u'statistics', u'referers', u'boards', u'sections', u'no_restrictions', u'no_captcha', u'no_delay', u'notifications',
        u'invites', u'manage_admins', u'permissions', u'settings', u'help', u'files', u'restrictions', u'revive_post', u'no_user_captcha',
        ]
    defaults_compound = [
        (u'member', [u'read', u'new_thread', u'new_reply']),
        (u'white',  [u'member', u'no_restrictions', u'no_captcha', u'no_delay', u'reputation']),
        (u'moderator', [u'white', u'delete_posts', u'delete_threads', u'revive_post', u'view_log', u'restrictions', u'sessions', u'see_invisible', u'view_deleted', u'manage_threads', u'edit_posts', u'files']),
        (u'admin', [u'moderator', u'view_admins', u'statistics', u'referers', u'boards', u'sections', u'manage_archive', u'notifications', u'view_ip']),
        (u'root', [u'featured', u'admin', u'help', u'invites', u'manage_admins', u'permissions', u'settings']),
        ]
    def __init__(self):
        for name in self.defaults_simple:
            if not Permission.get(name):
                log.info("Created %s" % Permission(name))
        for name, includes_names in self.defaults_compound:
            perm = Permission.get(name)
            if not perm:
                log.info("Created %s" % CompoundPermission(name, includes_names=includes_names))
        self.load()

    def load(self):
        self.permissions = {}
        permissions = Permission.query.all()
        for permission in permissions:
            self.permissions[permission.name] = permission.expand()
        log.info(self.permissions)

    def process_admin_permissions(self, permissions):
        g = []
        b = {}
        for admin_permission in permissions:
            for permission in self.permissions[admin_permission.name]:
                if admin_permission.scope:
                    if not admin_permission.scope in b:
                        b[admin_permission.scope] = []
                    if not permission in b[admin_permission.scope]:
                        b[admin_permission.scope].append(permission)
                else:
                    if not permission in g:
                        g.append(permission)
        return (g, b)

class AdminPermission(meta.Declarative):
    __tablename__ = "admin_permissions"
    admin_permissions_id = Column(Integer, primary_key=True)
    admin_id             = Column(Integer, ForeignKey("admins.admin_id"), index=True)
    scope                = Column(Integer) # 0 for global, otherwise board_id
    name                 = Column(Unicode(16))

    @synonym_for('admin_permissions_id')
    @property
    def id(self):
        return self.admin_permissions_id
