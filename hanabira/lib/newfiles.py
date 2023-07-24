# -*- coding: utf-8 -*-
import logging
from pylons.i18n import _, ungettext, N_
from hanabira.model.files import File
from hanabira.model.threads import Post, Thread
from sqlalchemy.orm import eagerload
from hanabira.model import meta
import math, time, hashlib
log = logging.getLogger(__name__)

class NewFile(object):
    id = None
    key = None
    post_id = None
    filetype = None
    filename = None
    valid = False
    def __init__(self, id, post_id, filename, filetype, salt):
        self.id = id
        self.key = hashlib.sha256(str(long(time.time() * 10**7)) + hashlib.sha256(salt).hexdigest()).hexdigest()
        self.post_id = post_id
        self.filetype = filetype
        if type(filename) == str:
            filename = filename.decode('utf-8')
        self.filename = filename
        self.valid = True

class NewFiles(object):
    newfiles = []
    settings = None
    def __init__(self, settings):
        self.settings = settings
        
    def get(self, id, key):
        if len(self.newfiles) > id and self.newfiles[id].valid and self.newfiles[id].key == key:
            return self.newfiles[id]
        else:
            return None

    def new(self, post_id, filename, filetype):
        fid = len(self.newfiles)
        self.newfiles.append(NewFile(fid, post_id, filename, filetype, str(self.settings.security.hash.salt)))
        return self.newfiles[fid]
