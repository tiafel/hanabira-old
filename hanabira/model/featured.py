# -*- coding: utf-8 -*-
from hanabira.model.gorm import *
from hanabira.model.files import File
from hanabira.model.posts import Post

class Featured(meta.Declarative):
    __tablename__ = "featured"
    featured_id = Column(Integer, primary_key=True)
    post_id     = Column(Integer, ForeignKey('posts.post_id'), nullable=False)
    file_id     = Column(Integer, ForeignKey('files.file_id'), nullable=True)
    date        = Column(DateTime, nullable=False, index=True)
    show_text   = Column(Boolean, default=True)
    show_file   = Column(Boolean, default=True)
    thumb_path  = Column(UnicodeText, nullable=True)
    description = Column(UnicodeText, nullable=True)

    post        = relation(Post, lazy=False)
    file        = relation(File, lazy=False)
    
    @property
    def id(self):
        return self.featured_id

    @classmethod
    def new(cls, post_id, file_id=None, description=None, show_file=None, show_text=False):
        f = cls(post_id=post_id, description=description, date=datetime.datetime.now(), show_text=show_text)
        if file_id and show_file:
            file = File.get(file_id)
            # XXX: re-do image creation. Was 200x200 thumb at path = "/src/png/%sm.png" %  str(long(time.time() * 10**3))
            f.thumb_path = path
            f.show_file = True
            f.file_id = file_id
        meta.Session.add(f)
        meta.Session.commit()
