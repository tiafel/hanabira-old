# -*- coding: utf-8 -*-

from hanabira.model.gorm import *

from .filetype import Filetype
from .extensions import Extension

import logging
log = logging.getLogger(__name__)

class PickleWrapper(object):
    def dumps(self, *args, **kw):
        try:
            return pickle.dumps(*args, **kw)
        except Exception as e:
            return pickle.dumps(None)
            
    def loads(self, *args, **kw):
        try:
            return pickle.loads(*args, **kw)
        except Exception as e:
            return None

class File(meta.Declarative):
    __tablename__ = "files"
    thumbnail = None
    file_id              = Column(Integer, primary_key=True)
    path                 = Column(Unicode(255), nullable=False)
    size                 = Column(Integer, nullable=False)
    thumb_path           = Column(Unicode(255), nullable=False)
    thumb_width          = Column(Integer, nullable=False)
    thumb_height         = Column(Integer, nullable=False)
    filename             = Column(Unicode(64), nullable=False)
    timestamp            = Column(Unicode(32), nullable=False)
    metainfo             = Column(PickleType(pickler=PickleWrapper()), nullable=True)
    metainfo_raw         = Column(UnicodeText)
    date_added           = Column(DateTime)
    rating               = Column(Enum('unrated', 'sfw', 'r-15', 'r-18', 'r-18g', 'illegal'), nullable=False, default='unrated')
    ext_id               = Column(Integer, ForeignKey('extensions.ext_id'))
    filetype_id          = Column(Integer, ForeignKey('filetypes.filetype_id'))
    #_filetype_rel        = relation(Filetype, lazy=True)
    #extension            = relation(Extension, lazy=True)

    @synonym_for('file_id')
    @property
    def id(self):
        return self.file_id

    @classmethod
    def get(cls, file_id=None):
        if file_id:
            return cls.query.filter(cls.file_id == file_id).first()
        return None
    
    @property
    def filetype(self):
        ft = g.extensions.get_filetype(self)
        self.__dict__['filetype'] = ft
        return ft

    @property
    def extension(self):
        ext = g.extensions.ext_ids[self.ext_id]
        return ext

    def __init__(self, ext=None, temp_file=None, keep_filename=True):
        if ext and temp_file:
            self.temp_file = temp_file
            self.ext_id = ext.ext_id
            self.ext = ext
            self.filetype_id = ext.filetype_id
            self.size = self.temp_file.size
            self.date_added = self.temp_file.date
            self.rating = self.temp_file.rating
            self.filename = g.fs.filter_filename_orig(
                self.temp_file.filename_original)
            self.timestamp = self.temp_file.filename

    def process(self, *args, **kw):
        if self.filetype.process(self, *args, **kw):
            meta.Session.add(self)
            meta.Session.commit()

    @classmethod
    def handle_duplicates(cls, file1, file2):
        log.info("%s == %s" % (file1, file2))
        # Handle posts
        posts = file2.posts
        for post in posts:
            post.files.remove(file2)
            post.files.append(file1)
        # Handle fingerprints
        for fp in file2.fingerprints:
            fp.file_id = file1.id

        meta.Session.delete(file2)
        meta.Session.commit()
        
        
    @classmethod
    def reprocess(cls, f):
        # Rough version for now. Just update fingerprints and remove dupes
        new_fingerprints = []
        old_fingerprints = []
        for fp in f.fingerprints:
            old_fingerprints.append(fp.get_tuple())
        tf = g.fs.tf_from_file(f)
        fp1 = tf.get_fingerprint()
        if not fp1 in old_fingerprints:
            f2 = Fingerprint.get_file_by_tuple(fp1)
            if f2:
                return cls.handle_duplicates(file1=f2, file2=f)
            else:
                new_fingerprints.append(fp1)
        tf2, fpl, errors = f.filetype.preprocess(tf, f.extension, None)
        fp2 = tf2.get_fingerprint()
        if fp2 != fp1 and not fp2 in fpl:
            fpl.append(fp2)
        if not errors:
            for fp in fpl:
                if not fp in old_fingerprints and not fp in new_fingerprints:
                    f2 = Fingerprint.get_file_by_tuple(fp)
                    if f2:
                        return cls.handle_duplicates(file1=f2, file2=f)
                    else:
                        new_fingerprints.append(fp)
        if new_fingerprints:
            for fp in new_fingerprints:
                Fingerprint(t=fp, f=f)
        meta.Session.commit()
        
        

    def is_long(self):
        return self.filetype.is_long()

    def set_metainfo(self, metainfo):
        self.metainfo = metainfo
        self.metainfo_raw = "; ".join(map(str, metainfo.values()))

    def get_metadata(self):
        if not hasattr(self, 'metadata_dict'):
            self.metadata_dict = self.metainfo
        return self.metadata_dict
        
    def show_metadata(self):
        if not hasattr(self, 'metadata_html'):
            metadata = self.get_metadata()
            if not metadata:
                metadata = {}
            #log.info("File {0.id}, {0.filename}".format(self))
            #log.info("MD: {0}".format(metadata))
            if not 'type' in metadata:
                metadata['type'] = self.filename.rsplit('.',1)[-1].capitalize()
            self.metadata_html = self.filetype.process_metadata(metadata, self)
            return self.metadata_html
        else:
            return self.metadata_html

    def onclick_handler(self, post):
        return self.filetype.onclick_handler(self, self.get_metadata(), post)

    def has_actions(self):
        return self.filetype.has_actions()
    def get_actions(self, post):
        return self.filetype.get_actions(self, self.get_metadata(), post)
    def get_superscription(self):
        if self.is_long():
            return u''
        else:
            return u'- %s'%self.filetype.get_superscription()

    def get_basename(self):
        name = self.filename.rsplit('.', 1)[0]
        suffix = find_suffix(name)
        if suffix:
            return suffix[0]
        else:
            return name
    def get_suffix(self):
        filename = self.path.split('/')[-1]
        name = filename.rsplit('.', 1)[0]
        suffix = g.fs.find_suffix(name)
        if suffix:
            return suffix[1]
        else:
            return ""

    @classmethod
    def get_query_with_ft(cls):
        return cls.query #.join(Filetype)

    def export_dict(self):
        r = {
            '__class__': 'File',
            'file_id':self.id, 'src':self.path, 'thumb':self.thumb_path, 'size':self.size,
             'thumb_width':self.thumb_width, 'thumb_height':self.thumb_height,
             'type':self.filetype.type, 'rating':self.rating, 'metadata':self.metainfo}
        if self.rating == 'illegal':
            r['src'] = ''
            r['thumb'] = ''
        return r

    def __repr__(self):
        return "<File(%s, %s)>" % (self.file_id, self.path.encode('utf-8'))
