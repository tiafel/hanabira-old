# -*- coding: utf-8 -*-
from sqlalchemy import MetaData
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

__all__ = ['Session', 'engine', 'metadata', 'Declarative', 'globj']
engine = None
Session = scoped_session(sessionmaker())
metadata = MetaData()
globj = None

class DeclarativeBase(object):
    @classmethod
    def add_session(cls, session):
        cls.query = session.query_property()
        
    @classmethod
    def find(cls, id):
        return cls.query.filter(cls.id == id).first()
        
    def import_data(self, other, copy_id=True):
        if not copy_id:
            id_key = ['id', '%s_id'%self.__class__.__name__.lower()]
        for key in other.__class__.__mapper__.c._data:
            if copy_id or key not in id_key:
                self.__setattr__(key, other.__getattribute__(key))

    @property
    def _c(self):
        return self.__class__.__table__.c

Declarative = declarative_base(metadata=metadata, cls=DeclarativeBase)
