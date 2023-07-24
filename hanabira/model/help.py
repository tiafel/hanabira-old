# -*- coding: utf-8 -*-
import pickle
import logging
from docutils.core import publish_parts

from sqlalchemy import *
from sqlalchemy.orm import eagerload
from sqlalchemy.ext.declarative import synonym_for

from pylons.i18n import _, ungettext
from pylons import app_globals as g

from hanabira.model import meta

log = logging.getLogger(__name__)

class HelpArticle(meta.Declarative):
    __tablename__ = "help"
    help_id  = Column(Integer, primary_key=True)
    handle   = Column(Unicode(64), index=True, nullable=False)
    language = Column(Unicode(4), index=True, nullable=False, default='en')
    title    = Column(Unicode(128), nullable=False)
    text_raw = Column(UnicodeText, nullable=False)
    text     = Column(UnicodeText, nullable=False)
    markup   = Column(Enum('wakabamark', 'reStructuredText'), 
                      default='wakabamark')
    index    = Column(Integer, index=True, nullable=False)
    
    def parse(self):
        if self.markup == 'wakabamark':
            parsed = g.parser.parse_alone(self.text_raw)
            self.text = parsed.message
        elif self.markup == 'reStructuredText':
            parsed = publish_parts(self.text_raw, writer_name="html")
            self.text = parsed['html_body']
