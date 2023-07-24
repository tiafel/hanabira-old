# -*- coding: utf-8 -*-
import datetime, math, cgi, os, random
import cPickle as pickle
import logging

from sqlalchemy import *
from sqlalchemy.orm import eagerload, relation
from sqlalchemy.ext.declarative import synonym_for
from sqlalchemy.sql import and_, or_, not_, func

from pylons.i18n import _
from pylons import url, app_globals as g, session

from hanabira.model import meta

log = logging.getLogger(__name__)

class Tag(meta.Declarative):
    __tablename__ = "tags"
    tag_id  = Column(Integer, primary_key=True)
    tag     = Column(Unicode(128), nullable=False, index=True)
    title   = Column(UnicodeText)
    description = Column(UnicodeText)
    single_thread = Column(Boolean, default=True)
    threads = Column(Integer, default=0)
    follows = Column(Integer, default=0)
    autohides = Column(Integer, default=0)
    override_allow_names = Column(Integer, default=-1)
    override_restrict_trip = Column(Integer, default=-1)
    override_allow_OP_moderation = Column(Integer, default=-1)
    override_default_name = Column(UnicodeText)
    override_ignore_filters = Column(Integer, default=-1)
    override_require_captcha = Column(Integer, default=-1)
    override_confirm_bump_age = Column(Integer, default=-1)
    override_require_post_file = Column(Integer, default=-1)
    override_archive = Column(Integer, default=-1)
    override_allow_delete_threads = Column(Integer, default=-1)
    

    @synonym_for('tag_id')
    @property
    def id(self):
        return self.tag_id

    def export_dict(self, **kw):
        return dict(
            tag_id=self.id,
            tag=self.tag,
            title=self.title,
            description=self.description,
            )
    
