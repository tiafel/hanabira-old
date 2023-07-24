# -*- coding: utf-8 -*-

from hanabira.model.gorm import *
from pylons.i18n import _, ungettext, N_, set_lang
from hanabira.lib.utils import popen

from .filetype import Filetype

import logging
log = logging.getLogger(__name__)

def archive_tar(filepath):
    r = popen("tar --list -f \"%s\"" % (filepath), 1)
    return list(filter(lambda x: x, r.split('\n')))

def archive_rar(filepath):
    r = popen("unrar vb \"%s\"" % (filepath), 1)
    return list(filter(lambda x: x, r.split('\n')))

def archive_zip(filepath):
    r = popen("unzip -ql \"%s\"" % (filepath), 1)
    return list(map(lambda x: " ".join(x[3:]), filter(lambda x: len(x) > 3, map(lambda x: x.split(), r.split('\n')))[2:]))

def archive_7z(filepath):
    r = popen("7z l \"%s\"" % (filepath), 1)
    #l = filter(lambda x: len(x) > 4, map(lambda x: x.split(), r.split('\n')))[4:-2]
    #files = []
    #for f in l:
    #    files.append((f[-1], f[3], ' '.join(f[:2])))
    #return files
    return list(map(lambda x: " ".join(x[5:]), filter(lambda x: len(x) > 5, map(lambda x: x.split(), r.split('\n')))[2:-1]))

class ArchiveFile(Filetype):
    __mapper_args__ = {'polymorphic_identity': u'archive'}
    fmap = {
        'tgz': archive_tar,
        'tar': archive_tar,
        'gz' : archive_tar,
        'bz2': archive_tar,
        'tbz': archive_tar,
        'rar': archive_rar,
        'zip': archive_zip,
        '7z' : archive_7z,
        }
    
    def process(self, file, thumb_res, fileset):
        metadata = {'type':'Archive'}
        if file.temp_file.ext in self.fmap:
            files = self.fmap[file.temp_file.ext](file.temp_file.path)
            files.sort()
            metadata['files'] = files
            metadata['files_count'] = len(files)
        else:
            raise Exception(_("unknown archive type"))        
        return Filetype.process(self, file, thumb_res, fileset, metadata)

    def process_metadata(self, metadata, file):
        if metadata is None:
            metadata = {}
        return _("%s, %.2f KB, %s files") % (metadata.get('type', 'unknown'), (file.size / 1024.0), metadata.get('files_count', 0))

    def onclick_handler(self, file, metadata, post):
        return u"open_url('%s', '_blank')" % (url('util_archive_view', file_id=file.id, post_id=post.id))

    def get_actions(self, file, metadata, post):
        return [
            {'action':'view', 'class':'view_', 'url':url('util_archive_view', file_id=file.id, post_id=post.id)},
            ]
    def has_actions(self):
        return True
