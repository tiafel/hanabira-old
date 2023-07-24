# -*- coding: utf-8 -*-

from hanabira.model.gorm import *

log = logging.getLogger(__name__)

class Channel(meta.Declarative):
    __tablename__ = "chans"
    chan_id = Column(Integer, primary_key=True)
    name    = Column(UnicodeText, nullable=False)
    title      = Column(UnicodeText, nullable=False)
    host     = Column(UnicodeText, nullable=False)
    lower_banner = Column(UnicodeText)

    @synonym_for('chan_id')
    @property
    def id(self):
        return self.chan_id
    
    @property
    def upper_banner():
        img = random.choice(meta.upper_banners)
        return '<img href="%s" /><br />'%img
        
    def __repr__(self):
        return "<Channel %s @ %s>"%(self.title.encode('utf-8'), self.name.encode('utf-8'))

class Section(meta.Declarative):
    __tablename__ = "sections"
    section_id = Column(Integer, primary_key=True)
    title      = Column(UnicodeText, nullable=False)
    index      = Column(Integer)
    chan_id   = Column(Integer, ForeignKey("chans.chan_id"), nullable=False, index=True)
    chan       = relation(Channel)

    @synonym_for('section_id')
    @property
    def id(self):
        return self.section_id

    @property
    def channel(self):
        return g.boards.chan_ids[self.chan_id]
    
    def __repr__(self):
        return u"<Section(%s)[%s][%s]>" % (unicode(self.title), self.section_id, self.chan_id)

    def __str__(self):
        return self.title

    def __unicode__(self):
        return self.title

