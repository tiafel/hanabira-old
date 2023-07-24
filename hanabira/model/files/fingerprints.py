# -*- coding: utf-8 -*-

from hanabira.model.gorm import *

from .files import File

import logging
log = logging.getLogger(__name__)

class Fingerprint(meta.Declarative):
    __tablename__ = "fingerprints"
    fingerprint_id = Column(Integer, primary_key=True)
    file_id        = Column(Integer, ForeignKey("files.file_id"))
    type           = Column(String(8), nullable=False)
    quantifier     = Column(Integer)
    fingerprint    = Column(String(64), nullable=False)

    file           = relation(File, backref='fingerprints')

    @synonym_for('fingerprint_id')
    @property
    def id(self):
        return self.fingerprint_id

    def __init__(self, t, f):
        self.file_id = f.file_id
        self.type = t[0]
        self.quantifier = t[1]
        self.fingerprint = t[2]
        meta.Session.add(self)
        meta.Session.commit()

    @classmethod
    def get_file(cls, type, quantifier, fingerprint):
        fp = cls.query.filter(cls.type == type).filter(cls.quantifier == quantifier).filter(cls.fingerprint == fingerprint).first()
        if fp:
            return fp.file

    @classmethod
    def get_file_by_tuple(cls, tpl):
        return cls.get_file(tpl[0], tpl[1], tpl[2])

    def get_tuple(self):
        return (self.type, self.quantifier, self.fingerprint)

    def __repr__(self):
        return "<Fingerprint%s>" % (str(self.get_tuple()))

Index('idx_file_fingerprint', Fingerprint.type, Fingerprint.quantifier, Fingerprint.fingerprint, unique=True)