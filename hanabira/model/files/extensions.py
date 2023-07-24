# -*- coding: utf-8 -*-
from PIL import Image
from hanabira.model.gorm import *

from .filetype import Filetype
from .images import ImageFile, VectorFile
from .music import MusicFile
from .archive import ArchiveFile
from .flash import FlashFile
from .pdf import PDFFile
from .text import TextFile, CodeFile
from .video import VideoFile

import logging
log = logging.getLogger(__name__)

class Extension(meta.Declarative):
    __tablename__ = "extensions"
    ext_id      = Column(Integer, primary_key=True)
    thumb_path  = Column(Unicode(255), nullable=True)
    ext         = Column(Unicode(16), nullable=False, unique=True, index=True)
    filetype_id = Column(Integer, ForeignKey('filetypes.filetype_id'), nullable=False)
    filetype    = relation(Filetype)
    
    @synonym_for('ext_id')
    @property
    def id(self):
        return self.ext_id
    
    def __init__(self, ext=None, type=None, thumb=None):
        if ext and type:
            self.ext = ext
            self.filetype_id = g.extensions.types[type].filetype_id
            if thumb:
                self.thumb_path = thumb
            meta.Session.add(self)
            meta.Session.commit()
        
    def load(self):
        if self.thumb_path and not hasattr(self, 'thumb_width'):
            img = Image.open(g.fs.local(self.thumb_path))
            self.thumb_width = img.size[0]
            self.thumb_height = img.size[1]
            img.close()
            
class Extensions(object):
    types = {'image':ImageFile, 'vector':VectorFile, 'flash':FlashFile, 
             'music':MusicFile, 'video': VideoFile, 
             'text':TextFile, 'code':CodeFile, 'archive':ArchiveFile, 
             'pdf':PDFFile}
    exts = {}
    ext_ids = {}
    filetype_ids = {}
    def __init__(self):
        for t in self.types:
            tobj = Filetype.query.filter(Filetype.type == t).first()
            if not tobj:
                tobj = self.types[t]()
                meta.Session.add(tobj)
                meta.Session.commit()
            self.types[t] = tobj
            self.filetype_ids[tobj.id] = tobj
        exts = Extension.query.options(eagerload('filetype')).all()
        for ext in exts:
            ext.load()
            self.exts[ext.ext] = ext
            self.ext_ids[ext.id] = ext

    def get_ext(self, filename, allowed_filetypes):
        ext = filename.rsplit('.',1)[1:]
        ext = ext and ext[0].lower() or ''
        if ext in self.exts:
            if self.exts[ext].filetype.type in allowed_filetypes:
                return self.exts[ext]
            else:
                return False
        else:
            return False
        
    def get_filetype(self, f):
        return self.filetype_ids[f.filetype_id]

    def get_file(self, fobj, allowed_filetypes, keep_filename):
        if isinstance(fobj, cgi.FieldStorage):
            ext = fobj.filename.rsplit('.',1)[1:]
            ext = ext and ext[0].lower() or ''
            if ext in self.exts:
                if self.exts[ext].filetype.type in allowed_filetypes:
                    f = File(self.exts[ext], fobj, keep_filename=keep_filename)
                    f2 = File.query.filter(File.ext_id == f.ext_id).filter(File.fingerprint == f.fingerprint).first()
                    if f2:
                        return f2
                    else:
                        return f
                else:
                    return False
            else:
                return False
        else:
            return False
