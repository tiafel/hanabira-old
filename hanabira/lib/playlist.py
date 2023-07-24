# -*- coding: utf-8 -*-
from pylons import app_globals as g
from hanabira.model import meta
import simplejson
import logging
log = logging.getLogger(__name__)

class PlayListItem(object):
    file_id = None
    path    = None
    filename= None
    duration= None
    name    = None
    ext     = None
    idx     = 0
    def __init__(self, f):
        self.file_id = f.id
        self.path    = g.fs.web(f.path)
        self.filename = f.filename
        self.duration = int(f.metainfo['length'])
        self.name    = f.filename
        self.ext     = f.extension.ext

    def export(self):
        return self.__dict__
        
class PlayList(object):
    playlist = None
    index    = None
    def __init__(self, default=None):
        self.playlist = []
        self.index    = {}
        if default:
            for f in default:
                item = PlayListItem(f)
                self.playlist.append(item)
                self.index[f.id] = item
            self.reindex()

    def reindex(self):
        for i in range(len(self.playlist)):
            self.playlist[i].idx = i
            

    def add(self, f):
        if not f.id in self.index:
            item = PlayListItem(f)
            self.playlist.append(item)
            self.index[f.id] = item
            self.reindex()

    def remove(self, file_id):
        if file_id in self.index:
            item = self.index[file_id]
            self.playlist.remove(item)
            del self.index[file_id]
            self.reindex()

    def export(self):
        l = [x.export() for x in self.playlist]
        return simplejson.dumps(l)
            
            
