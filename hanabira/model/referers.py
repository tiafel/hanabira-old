# -*- coding: utf-8 -*-
from sqlalchemy import *
from sqlalchemy.orm import eagerload, relation
from sqlalchemy.ext.declarative import synonym_for
from sqlalchemy.dialects.mysql.base import BIGINT
from hanabira.model import meta
from datetime import datetime
import hashlib, random, string, time
from pylons.i18n import _, ungettext
import logging
log = logging.getLogger(__name__)

class Referer(meta.Declarative):
    __tablename__ = "referers"
    referer_id    = Column(Integer, primary_key=True)
    domain        = Column(Unicode(64), nullable=False, index=True)
    date          = Column(DateTime)
    referer       = Column(UnicodeText)
    target        = Column(UnicodeText)
    ip            = Column(BIGINT, ForeignKey('ips.ip'), nullable=True, index=True)
    session_id    = Column(String(64), nullable=False)
    session_new   = Column(Boolean, default=False)
    
    @synonym_for('referer_id')
    @property
    def id(self):
        return self.referer_id
    
    def commit(self):
        meta.Session.add(self)
        meta.Session.commit()


