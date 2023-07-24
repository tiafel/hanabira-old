# -*- coding: utf-8 -*-

import datetime

from sqlalchemy import *
from sqlalchemy.orm import eagerload, relation
from sqlalchemy.sql import and_, or_, not_, func
from sqlalchemy.ext.declarative import synonym_for
from sqlalchemy.dialects.mysql.base import BIGINT

from hanabira.model import meta

import logging

log = logging.getLogger(__name__)

class Notification(meta.Declarative):
    __tablename__ = "notifications"
    notification_id = Column(Integer, primary_key=True)
    session_id      = Column(Integer, ForeignKey('sessions.session_id'))
    parent_id       = Column(Integer)
    created_at      = Column(DateTime)
    unread          = Column(Boolean, default=True)
    text            = Column(UnicodeText)
    text_raw        = Column(UnicodeText)
    level           = Column(Enum('info', 'warning', 'message'))

    @synonym_for('notification_id')
    @property
    def id(self):
        return self.notification_id

    def __init__(self, session, text, text_raw=None,
                 level='message', parent_id=0):
        self.session_id = session.id
        self.text = text
        self.text_raw = text_raw
        self.level = level
        self.parent_id = parent_id
        self.unread = True
        self.created_at = datetime.datetime.now()

    def export_dict(self, **kw):
        return dict(
            notification_id=self.id,
            text=self.text,
            text_raw=self.text_raw,
            level=self.level,
            created_at=str(self.created_at),
            parent_id=self.parent_id,
            unread=self.unread
            )
