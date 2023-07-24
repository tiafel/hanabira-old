# -*- coding: utf-8 -*-
from pygments.lexers import get_lexer_for_filename, get_lexer_by_name, TextLexer
from pygments import highlight
from pygments.formatters import ImageFormatter
from pylons.i18n import _, ungettext, N_, set_lang

from hanabira.model.gorm import *
from hanabira.lib.utils import fix_charset, fix_charset_unicode

from .filetype import Filetype

import logging
log = logging.getLogger(__name__)

class TextFile(Filetype):
    __mapper_args__ = {'polymorphic_identity': u'text'}
    font_name = "VL PGothic"
    def fix_file(self, filepath):
        cont = open(filepath, 'r').read()
        res = fix_charset(cont)
        res = res.replace("\r\n", "\n").replace("\r", "\n").rstrip()
        lines = res.split("\n")
        lines_qty = len(lines)
        return (res, lines_qty, lines)

    def get_thumb(self, filepath, text, lexer):
        imgfrm = ImageFormatter(line_pad=1, font_size=8, line_numbers=False, font_name=self.font_name, image_pad=0)
        txt_path = g.fs.new_temp_path('png')
        txt_img = highlight(text, lexer, imgfrm, outfile=txt_path)
        # XXX: make thumb out of txt_path image
        # Overlay it with g.fs.local(g.settings.file.text.bg_file)
        #                 g.fs.local(g.settings.file.text.ov_file)
        #g.settings.file.text.width
        #g.settings.file.text.height
        #g.settings.file.text.x_offset
        #g.settings.file.text.y_offset
        os.unlink(txt_path)
        raise Exception("Currently not supported")
        return imgbg

    def process(self, file, thumb_res, fileset):
        res = self.fix_file(file.temp_file.path)
        fw = open(file.temp_file.path, 'w+b')
        fw.write(res[0].encode('utf8'))
        fw.close()
        if res[1] > 20:
            txt = "\n".join(map(lambda x: x.rstrip(), res[2][0:20]))
        else:
            txt = "\n".join(map(lambda x: x.rstrip(), res[2]))
        if txt:
            thumb = self.get_thumb(file.temp_file.path, txt, TextLexer())
        else:
            raise Exception(_("file is empty"))
        metainfo = {'type':'Text', 'lines':res[1]}
        thumb_path = g.fs.new_temp_path('png')
        file.thumbnail = self.make_thumb(thumb, thumb_path, 'png', thumb_res)
        return Filetype.process(self, file, thumb_res, fileset, metainfo)

    def process_file(self, filepath, ext):
        return metainfo, thumb
    
    def process_metadata(self, metadata, file):
        return _("%s, %.2f KB, %s lines") % (metadata['type'], (file.size / 1024.0), metadata['lines'])

    def onclick_handler(self, file, metadata, post):
        return u"open_url('%s', '_blank')" % (url('util_text_view', file_id=file.id, post_id=post.id))

    def get_actions(self, file, metadata, post):
        return [
            {'action':'view', 'class':'view_', 'url':url('util_text_view', file_id=file.id, post_id=post.id)},
            {'action':'edit', 'class':'edit_', 'url':url('util_text_edit', file_id=file.id, post_id=post.id)},
            ]
    
    def has_actions(self):
        return True
    
class CodeFile(TextFile):
    __mapper_args__ = {'polymorphic_identity': u'code'}
    font_name = "dejavu sans mono"
    def process(self, file, thumb_res, fileset):
        res = self.fix_file(file.temp_file.path)
        fw = open(file.temp_file.path, 'w+b')
        fw.write(res[0].encode('utf8'))
        fw.close()
        lexer = get_lexer_for_filename(file.temp_file.path)
        if res[1] > 20:
            txt = "\n".join(map(lambda x: x.rstrip(), res[2][0:20]))
        else:
            txt = "\n".join(map(lambda x: x.rstrip(), res[2]))
        if txt:
            thumb = self.get_thumb(file.temp_file.path, txt, lexer)
        else:
            raise Exception(_("file is empty"))
        metainfo = {'type':lexer.name, 'lines':res[1]}
        thumb_path = g.fs.new_temp_path('png')
        file.thumbnail = self.make_thumb(thumb, thumb_path, 'png', thumb_res)
        return Filetype.process(self, file, thumb_res, fileset, metainfo)
