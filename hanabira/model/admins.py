# -*- coding: utf-8 -*-

from datetime import datetime
import hashlib, random, string, time
import logging

from sqlalchemy import *
from sqlalchemy.orm import eagerload, relation, reconstructor
from sqlalchemy.ext.declarative import synonym_for

from pylons.i18n import _, ungettext, N_
from pylons import app_globals as g

from hanabira.model import meta
from hanabira.model.logs import *
from hanabira.model.permissions import AdminPermission
log = logging.getLogger(__name__)

class Admin(meta.Declarative):
    """
    Admin class
    >>> a = Admin(login=u'testadmin', email=u'test@test.com', password='testpass')
    >>> a.valid()
    True
    """
    __tablename__ = "admins"
    admin_id    = Column(Integer, primary_key=True)
    login       = Column(Unicode(64), nullable=False, unique=True)
    password    = Column(String(128), nullable=False)
    email       = Column(Unicode(64), nullable=False, unique=True)
    enabled     = Column(Boolean, nullable=False, default=False)
    permissions = relation(AdminPermission)
    @synonym_for('admin_id')
    @property
    def id(self):
        return self.admin_id

    @classmethod
    def get_hash(cls, password):
        salt = hashlib.sha512(str(g.settings.security.hash.salt).encode('utf-8')).hexdigest()
        return hashlib.sha512((password + salt).encode('utf-8')).hexdigest()

    def __init__(self, login=None, email=None, password=None):
        if login and email and password:
            meta.Session.add(self)
            self.login = login
            self.email = email
            self.set_password(password)
    
    def set_password(self, password):
        self.password = self.get_hash(password)
        meta.Session.commit()

    @classmethod
    def get(cls, login, password):
        admin = cls.query.filter(cls.login == login).filter(cls.password == cls.get_hash(password)).first()
        return admin

    def add_key(self):
        keystr = hashlib.sha256(str(long(time.time() * 10**7))).hexdigest()
        key = AdminKey(admin_id = self.id, key=keystr)
        meta.Session.add(key)
        self.keys.append(key)
        meta.Session.commit()
        return key

    def valid(self):
        """
        Load self from db by id, and compare passwords
        """
        self2 = self.__class__.query.filter(self.__class__.admin_id == self.id).first()
        if self2:
            if self.password == self2.password and self.login == self2.login:
                return True
            else:
                return False
        else:
            return False

    def reload_permissions(self):
        permissions = AdminPermission.query.filter(AdminPermission.admin_id == self.id).all()
        self.global_permissions, self.board_permissions = g.permissions.process_admin_permissions(permissions)

    def add_permission(self, name, scope=0):
        ap = AdminPermission()
        ap.admin_id = self.admin_id
        ap.name = name
        ap.scope = scope
        meta.Session.add(ap)
        meta.Session.commit()
        self.reload_permissions()

    def delete_permission(self, ap_id):
        ap = AdminPermission.query.filter(AdminPermission.admin_id == self.id).filter(AdminPermission.admin_permissions_id == ap_id).first()
        if ap:
            meta.Session.delete(ap)
            meta.Session.commit()

    def has_permission(self, name, scope=0):
        # XXX: fix multiple lookup
        if isinstance(name, list):
            name = name[0]
            
        if name in self.global_permissions:
            return True
        elif scope and scope in self.board_permissions and name in self.board_permissions[scope]:
            return True
        else:
            return False
        
    def get_permission(self, name):
        if name in self.global_permissions:
            return [0]
        else:
            scopes = []
            for scope in self.board_permissions:
                if name in self.board_permissions[scope]:
                    scopes.append(scope)
            return scopes

    @reconstructor
    def construct(self):
        if self.admin_id:
            self.reload_permissions()
        else:
            self.global_permissions = []
            self.board_permissions = {}

class AdminKey(meta.Declarative):
    __tablename__ = "admin_keys"
    key_id   = Column(Integer, primary_key=True)
    key      = Column(String(64), nullable=False)
    admin_id = Column(Integer, ForeignKey("admins.admin_id"), index=True, nullable=False)

    admin    = relation(Admin, backref='keys', lazy=False)
    @synonym_for('key_id')
    @property
    def id(self):
        return self.key_id
