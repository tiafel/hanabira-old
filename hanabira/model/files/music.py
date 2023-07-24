# -*- coding: utf-8 -*-

import urllib.request, urllib.parse, urllib.error
import simplejson
from mutagen import mp3, mp4, flac, oggvorbis as ogg
from pylons.i18n import _, ungettext, N_, set_lang

from hanabira.model.gorm import *
from hanabira.lib.utils import fix_charset_unicode, fix_charset

from .filetype import Filetype

import logging
log = logging.getLogger(__name__)

def flac_tag(tag, meta):
    return meta[tag][0]
def id3_tag(tag, meta):
    return meta[tag].text[0]
def oggv_tag(tag, meta):
    return meta[tag][0]

class MusicFile(Filetype):
    __mapper_args__ = {'polymorphic_identity': 'music'}
    exts = {'ogg':ogg, 'flac':flac, 'mp3':mp3, 'mp4':mp4}
    gettag = {'VCFLACDict':flac_tag, 'ID3':id3_tag, 'OggVCommentDict': oggv_tag}
    tagidx = {'VCFLACDict':0, 'ID3':2, 'OggVCommentDict': 1}
    tags = {
        'artist': ([],[], ['TPE1']),
        'album': ([], [], ['TALB']),
        'title': ([], [], ['TIT2']),
        'totaltracks': ([], [], []),
        'tracknumber': ([], [], []),
        }
    def get_thumb(self, filepath, thumb_data, thumb_ext):
        thumb_path = g.fs.new_temp_path(thumb_ext)
        fw = open(thumb_path, 'w+b')
        fw.write(thumb_data)
        fw.close()
        # XXX: make proper thumb out of thumb_path (resize, get metadata)
        # XXX: overlay it with static_local(g.settings.file.sound.ov_file)
        raise Exception("Temporarily not supported")
        return img
        
    def process(self, file, thumb_res, fileset):
        metainfo, thumb = self.process_file(file.temp_file.path, file.ext.ext)
        if thumb:
            thumb_path = temp_file("%ss.%s" % (file.temp_file.name, 'png'))
            file.thumbnail = self.make_thumb(thumb, thumb_path, 'png', thumb_res)
        return Filetype.process(self, file, thumb_res, fileset, metainfo)

    def process_file(self, filepath, extension):
        meta = self.exts[extension].Open(filepath)
        metadata = {
            'type': type(meta).__name__,
            'sample_rate': meta.info.sample_rate,
            'length': meta.info.length,
            }
        if 'bitrate' in meta.info.__dict__:
            metadata['bitrate'] = meta.info.bitrate
        else:
            metadata['bitrate'] = meta.info.total_samples * meta.info.bits_per_sample / meta.info.length
            
        if not meta.tags:
            meta.tags = {}
        thumbnail = None
        img, ext = None, None
        if 'APIC:' in meta.tags:
            img = meta.tags['APIC:'].data
            ext = meta.tags['APIC:'].mime.split('/')[-1]
        elif hasattr(meta, 'pictures') and meta.pictures:
            img = meta.pictures[0].data
            ext = meta.pictures[0].mime.split('/')[-1]
        if img and ext:
            if ext == 'jpeg':
                ext = 'jpg'
            try:
                thumbnail = self.get_thumb(filepath, img, ext)
            except Exception:
                pass
            
        recoded = False
        if meta.tags:
            tagtype = type(meta.tags).__name__
            gettag = self.gettag[tagtype]
            tagidx = self.tagidx[tagtype]
            encoding = None
            for tag in self.tags:
                taglist = self.tags[tag][tagidx]
                if taglist:
                    for tag2 in taglist:
                        if tag2 in meta.tags:
                            metadata[tag], encoding = fix_charset_unicode(gettag(tag2, meta.tags), encoding)
                            if encoding and encoding != 'utf-8' or meta.tags[tag2].encoding != 3:
                                meta.tags[tag2].encoding = 3
                                meta.tags[tag2].text[0] = metadata[tag]
                                recoded = True
                                log.info("%s/%s => %s (%s) [%s]" % (tag, tag2, metadata[tag], type(metadata[tag]), encoding))
                            break
                else:
                    if tag in meta.tags:
                        metadata[tag], encoding = fix_charset_unicode(gettag(tag, meta.tags), encoding)
                        if encoding and encoding != 'utf-8':
                            meta.tags[tag][0] = metadata[tag]
                            recoded = True
                            log.info("%s => %s (%s) [%s]" % (tag, metadata[tag], type(metadata[tag]), encoding))

        if 'TRCK' in meta.tags:
            tracks = meta.tags['TRCK'].text[0].split('/')
            metadata['tracknumber'] = tracks[0]
            if len(tracks)>1:
                metadata['totaltracks'] = tracks[1]
            else:
                metadata['totaltracks'] = tracks[0]
        
        log.info(metadata)
        if recoded:
            meta.save()
        return metadata, thumbnail

    def process_metadata(self, metadata, file):
        fileinfo = "%s, %.2f KB, %d:%02d m @ %s/%s kHz" % (metadata['type'], (file.size / 1024.0), metadata['length']/60, metadata['length']%60, metadata['bitrate'] / 1000.0, metadata['sample_rate'] / 1000.0)
        artist = metadata.get('artist', 'Unknown')
        album = metadata.get('album', 'Unknown')
        title = metadata.get('title', 'Unknown')
        tn = metadata.get('tracknumber', '0')
        tc =  metadata.get('totaltracks', '0')
        trackinfo = "%s — %s / %s [%s/%s]" % (artist, album, title, tn, tc)
        return """
        %s <br/> %s
        """ % (fileinfo, trackinfo)
        
    def get_actions(self, file, metadata, post):
        if metadata['type'].lower() == 'oggvorbis':
            fmt = 'ogg'
        elif metadata['type'].lower() == 'mp3':
            fmt = 'mp3'
        else:
            fmt = '';
        path = urllib.parse.quote(file.path.encode('utf-8'))
        if fmt:
            item = {'file_id':file.id, 'path':g.fs.web(path), 'duration':int(file.metainfo['length']), 'filename':file.filename, 'name':file.filename, 'ext':file.extension.ext}
            item = simplejson.dumps(item).replace('"', "'")
            return [
                {'action':'add', 'class':'add_', 'click':"add_to_playlist(%s);" % (item)},
                {'action':'play', 'class':'play_', 'click':"play_at_playlist(%s);" % (item)},
                ]
        else:
            return []
    
    def has_actions(self):
        return True

    def is_long(self):
        return True