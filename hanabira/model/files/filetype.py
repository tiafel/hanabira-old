# -*- coding: utf-8 -*-

import traceback
from pylons.i18n import _, ungettext, N_, set_lang
from hanabira.model.gorm import *

import logging
log = logging.getLogger(__name__)

class Filetype(meta.Declarative):
    __tablename__ = "filetypes"
    filetype_id = Column(Integer, primary_key=True)
    type        = Column(Unicode(16), nullable=False)
    
    __mapper_args__ = {'polymorphic_on': type, 'polymorphic_identity': u'none'}
    
    @synonym_for('filetype_id')
    @property
    def id(self):
        return self.filetype_id

    # Do rough file preprocessing, no File() instance yet.
    # Returns tempfile, fingerprint list, errors
    def preprocess(self, tf, ext, board):
        return (tf, [], None)
    
    def process(self, file, thumb_res, fileset, metadata={}):
        if not file.thumb_path:
            if file.thumbnail:
                file.thumb_path = u"thumb/%s/%02d%02d/%ss.%s" % (file.ext.ext, file.date_added.year%100, file.date_added.month, file.temp_file.name, file.thumbnail.ext)
                file.thumb_width = file.thumbnail.width
                file.thumb_height = file.thumbnail.height
                file.thumbnail.save(g.fs.local(file.thumb_path))
            else:
                file.thumb_path = file.ext.thumb_path
                file.thumb_width = file.ext.thumb_width
                file.thumb_height = file.ext.thumb_height
        file.set_metainfo(metadata)
        parent = "src/%s/%02d%02d/" % (file.ext.ext, file.date_added.year%100, file.date_added.month)
        filename = g.fs.make_filename(file, parent)
        path = "%s%s" % (parent, filename)
        file.path = path
        file.temp_file.save(g.fs.local(path))
        return True
 
    def reprocess(self, file):
        pass

    def fingerprint(self, file):
        return file.temp_file.get_fingerprint()

    def process_metadata(self, metadata, file):
        return u"%s, %.2f KB" % (metadata['type'], (file.size / 1024.0))

    def onclick_handler(self, file, metadata, post):
        return u""

    def has_actions(self):
        return False
    def get_actions(self, file, metadata, post):
        return []
    def get_superscription(self):
        return _("Click the image to get file")

    def is_long(self):
        return False

    def make_thumb(self, img, path, ext, thumb_res):
        geom = img.size
        width, height = geom
        if width > thumb_res or height > thumb_res:
            img.thumbnail((thumb_res, thumb_res))#$"%sx%s" % (thumb_res, thumb_res))
            geom = img.size
        try:
            img.save(path)
            return g.fs.thumbnail(path, ext, geom[0], geom[1])
        except Exception as e:
            log.info("Exception: %s" % e)
            traceback.print_exc()      
