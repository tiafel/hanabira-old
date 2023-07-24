# -*- coding: utf-8 -*-

from pylons.i18n import _, ungettext, N_, set_lang
from hanabira.model.gorm import *

from .filetype import Filetype
from hanabira.lib.utils import popen

import logging
log = logging.getLogger(__name__)

class VideoFile(Filetype):
    __mapper_args__ = {'polymorphic_identity': u'video'}
    def process(self, file, thumb_res, fileset):
        log.debug('Processing %s[0], %s bytes' % (file.temp_file.path, file.temp_file.size))
        r = popen('exiftool "{0}"'.format(file.temp_file.path))
        if not "video/" in r or not 'Duration' in r or not "Image Size" in r:
            raise Exception("Not a video file!")
        meta = {}
        for line in r.strip().split("\n"):
            if not ":" in line:
                continue
            k,v = line.split(":", 1)
            meta[k.strip()] = v.strip()
        
        print(meta)
        w,h = map(int, meta['Image Size'].split('x'))
        sf = float(w) / h
        print(w,h,sf,thumb_res)
        if w > h:
            th_w = thumb_res
            th_h = int(float(th_w) / sf)
        else:
            th_h = thumb_res
            th_w = int(th_h * sf)
        thumb_path = g.fs.new_temp_path('jpg')
        r = popen('ffmpeg -ss 0.5 -i "{0}" -vframes 1 -s {1}x{2} -f image2 {3}'.format(file.temp_file.path, th_w, th_h, thumb_path))
        if not os.path.exists(thumb_path):
            raise Exception("Could not create thumbnail!")
        file.thumbnail = g.fs.thumbnail(thumb_path, 'jpg', th_w, th_h)
        return Filetype.process(self, file, thumb_res, fileset, meta)

    def process_metadata(self, metadata, file):
        return "Video {0[Image Size]} x {0[Duration]}; {0[File Size]}".format(metadata)

    def get_superscription(self):
        return _("Click the image to play video")
