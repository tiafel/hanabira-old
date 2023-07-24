# -*- coding: utf-8 -*-
from hanabira.model.gorm import *

from .filetype import Filetype

import logging
log = logging.getLogger(__name__)

class PDFFile(Filetype):
    __mapper_args__ = {'polymorphic_identity': u'pdf'}
    def process(self, file, thumb_res, fileset):
        log.debug('Processing %s[0], %s bytes' % (file.temp_file.path, file.temp_file.size))
        # XXX: make thumbnail
        # get metadata
        """
        f = open(file.temp_file.path)
        pdf = pyPdf.PdfFileReader(f)
        if pdf.isEncrypted:
            secured = True
            log.debug('file unreadable for pypdf, reading by magick')
            r = popen('identify -density "2x2" -format ";%%p" "%s"' % (file.temp_file.path), 1)
            pages = safe_int(r.split(';')[-1])
        else:
            secured = False
            pages = pdf.getNumPages()
        f.close()
        metainfo = {'type':'PDF', 'pages':pages, 'width':width, 'height':height, 'secured':secured}
        thumb_path = g.fs.new_temp_path('jpg')
        file.thumbnail = self.make_thumb(img, thumb_path, 'jpg', thumb_res)
        return Filetype.process(self, file, thumb_res, fileset, metainfo)
        """
        raise Exception("Currently not supported")

    def process_metadata(self, metadata, file):
        pages = metadata['pages'] and ungettext(', %s page', ', %s pages', metadata['pages'])%metadata['pages'] or ''
        secured = metadata['secured'] and ' [secured]' or ''
        return u"%s, %.2f KB, %s×%s%s%s" % (metadata['type'], (file.size / 1024.0), metadata.get('width', 0), metadata.get('height', 0), pages, secured)
