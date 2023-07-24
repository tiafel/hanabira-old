# -*- coding: utf-8 -*-
from sqlalchemy import *
from sqlalchemy.ext.declarative import synonym_for
from pylons import url, app_globals as g, session
from hanabira.model import meta
import datetime
import time
import hashlib
import logging
log = logging.getLogger(__name__)

class Invite(meta.Declarative):
    __tablename__ = "invites"
    invite_id = Column(Integer, primary_key=True)
    invite    = Column(String(128), nullable=False, unique=True)
    date      = Column(DateTime,  nullable=False)
    
    @synonym_for('invite_id')
    @property
    def id(self):
        return self.invite_id
    
    def __init__(self):
        self.date = datetime.datetime.now()
        self.invite = self.generate_code()
        meta.Session.add(self)
        meta.Session.commit()

    @classmethod
    def get(cls, code):
        invite = cls.query.filter(cls.invite==code).first()
        ret = False
        if invite:
            ret = invite.id
            meta.Session.delete(invite)
            meta.Session.commit()
        return ret

    def generate_code(self):
        return hashlib.sha512(str(long(time.time() * 10**7)) + hashlib.sha512(str(g.settings.security.hash.salt)).hexdigest()).hexdigest()
