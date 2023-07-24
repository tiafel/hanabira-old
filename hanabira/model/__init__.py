import sqlalchemy as sa
from sqlalchemy import orm
from hanabira.model import meta
from hanabira.model.posts import Post, DeletedPost, PostReference, PostRevision
from hanabira.model.threads import Thread, DeletedThread
from hanabira.model.featured import Featured
from hanabira.model.admins import *
from hanabira.model.boards import Board, Channel, Section
from hanabira.model.files import Filetype, File, Fingerprint, Extension
from hanabira.model.settings import Setting
from hanabira.model.invites import *
from hanabira.model.permissions import *
from hanabira.model.help import HelpArticle
from hanabira.model.restrictions import Restriction, Restrictions
from hanabira.model.referers import Referer
from hanabira.model.logs import IP, BaseEventLog
from hanabira.model.warnings import WarningRecord

import logging
log = logging.getLogger(__name__)

model_classes = [Permission, Restriction, Setting,
                 Channel, Section, Board,
                 Admin, AdminKey, AdminPermission, Invite,
                 Post, Thread, PostReference, Featured, PostRevision,
                 File, Fingerprint, Extension, Filetype,
                 HelpArticle, 
                 Referer, BaseEventLog, IP,
                 WarningRecord,
                 ]

def init_model(engine):
    sm = orm.sessionmaker(autoflush=False, autocommit=False, expire_on_commit=False, bind=engine)
    meta.engine = engine
    meta.Session = orm.scoped_session(sm)
    
    for cls in model_classes:
        cls.add_session(meta.Session)
