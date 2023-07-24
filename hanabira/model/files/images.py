# -*- coding: utf-8 -*-
from pylons.i18n import _, ungettext, N_, set_lang
from hanabira.model.gorm import *
from hanabira.lib.utils import popen
from hanabira.lib.helpers import static_domain
from PIL import Image
from .filetype import Filetype
import logging
import warnings
log = logging.getLogger(__name__)

warnings.simplefilter('error', Image.DecompressionBombWarning)

class ImageFile(Filetype):
    __mapper_args__ = {'polymorphic_identity': u'image'}
    def preprocess(self, tf, ext, board):
        if ext.ext == 'jpeg':
            tf.change_ext('jpg')
        img = Image.open(tf.path)
        log.info("Image.format={}".format(img.format)) 
        # PNG GIF JPEG
        # check img format
        w, h = img.size
        resolution = h*w
        if board:
            if board.file_max_res and board.file_max_res < resolution:
                return (tf, [], ['image resolution (%s pixels) is too big' % resolution])
            if board.file_min_res > resolution:
                return (tf, [], ['image resolution (%s pixels) is too small' % resolution])
        # fingerprinting
        return (tf, [], None)
    
    def process(self, file, thumb_res, fileset):
        img = Image.open(file.temp_file.path)
        geom = img.size
        width, height = geom
        file.metainfo = {'width':width, 'height':height}
        #ext = img.matte() and 'png' or 'jpg'
        ext = "png"
        thumb_path = g.fs.new_temp_path(ext)
        file.thumbnail = self.make_thumb(img, thumb_path, ext, thumb_res)
        return Filetype.process(self, file, thumb_res, fileset, file.metainfo)
        
    def get_superscription(self):
        return _("Click the image to expand")

    def process_metadata(self, metadata, file):
        return u"%s, %.2f KB, %s×%s" % (metadata['type'], (file.size / 1024.0), metadata['width'], metadata['height'])

    def onclick_handler(self, file, metadata, post):
        return u"expand_image(event, %s, %s)" % (metadata['width'], metadata['height'])

    def get_actions(self, file, metadata, post):
        imgurl = static_domain(file.path)
        return [
            {'action':'edit', 'class':'edit_', 'url':url('util_image_edit', file_id=file.id, post_id=post.id)},
            {'action':'Find source with google', 'class':'search_google', 'url': "http://www.google.com/searchbyimage?image_url=" + imgurl, 'new_tab':True},
            {'action':'Find source with iqdb', 'class': 'search_iqdb', 'url': "http://iqdb.org/?url=" + imgurl, 'new_tab':True},
            ]
    
    def has_actions(self):
        return True
        
class VectorFile(Filetype):
    __mapper_args__ = {'polymorphic_identity': u'vector'}
    def process(self, file, thumb_res, fileset):
        png_path = g.fs.new_temp_path('png')
        raise Exception("Currently not supported")
        # XXX: render as png
        metadata = {'width':width, 'height':height}
        thumb_path = g.fs.new_temp_path('png')
        file.thumbnail = self.make_thumb(img, thumb_path, 'png', thumb_res)
        os.unlink(png_path)
        return Filetype.process(self, file, thumb_res, fileset, metadata)        
        
    def get_superscription(self):
        return _("Click the image to expand")

    def process_metadata(self, metadata, file):
        return u"%s, %.2f KB, %s×%s" % (metadata['type'], (file.size / 1024.0), metadata['width'], metadata['height'])
    
