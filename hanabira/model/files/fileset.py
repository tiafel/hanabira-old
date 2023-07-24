# -*- coding: utf-8 -*-

import traceback
from pylons.i18n import _, ungettext, N_, set_lang
from hanabira.model.gorm import *

from .fingerprints import Fingerprint
from .ratings import ratings
from .files import File

import logging
log = logging.getLogger(__name__)

class FileSet(object):
    def __init__(self, fileset=None, board=None):
        if not fileset:
            fileset = []
        self.fingerprints = []
        self.fileset = fileset
        if self.fileset:
            for f in self.fileset:
                for fp in f.fingerprints:
                    self.fingerprints.append(fp.get_tuple())
        self.board = board
        self.errors = []
        self.filetypes = board.allowed_filetypes
        self.keep_filenames = board.keep_filenames
        
    def add_from_post(self, params):
        files = []
        file_count = int(params.get('post_files_count', "0"))
        if file_count > self.board.files_max_qty:
            file_count = self.board.files_max_qty
        for fi in range(1, file_count + 1):
            f = params.get('file_'+str(fi), None)
            if isinstance(f, cgi.FieldStorage):
                rating = params.get('file_%s_rating' % fi, 'unrated').lower()
                if rating == 'illegal' or not rating in ratings:
                    rating = 'unrated'
                self.add_from_fobj(f, rating)

    def add_from_fobj(self, fobj, rating='unrated'):
        fobj.filename = filename = g.fs.filter_filename(fobj.filename)
        try:
            ext = g.extensions.get_ext(filename, allowed_filetypes=self.filetypes)
            if ext:
                tf = g.fs.store_temp_file(fobj=fobj, ext=ext.ext, rating=rating)
                if tf.get_fingerprint() in self.fingerprints:
                    pass
                else:
                    if self.board.file_min_size <= tf.size and tf.size <= self.board.file_max_size:
                        return self.add_file(tf, ext)
                    elif self.board.file_max_size < tf.size:
                        self.errors.append(_('%s: file (%.2f kb) is too big') % (filename, tf.size/1024.0))
                    elif self.board.file_min_size > tf.size:
                        self.errors.append(_('%s: file (%.2f kb) is too small') % (filename, tf.size/1024.0))
            else:
                self.errors.append(_('%s: unknown file type') % filename)
        except Exception as e:
            log.info(u"Exception(): {0}".format(e))
            traceback.print_exc()
            self.errors.append(u'{0}: exception - {1}'.format(filename, e))
        return None       

    def add_from_data(self, data, filename, binary=False):
        try:
            ext = g.extensions.get_ext(filename, allowed_filetypes=self.filetypes)
            if ext:
                tf = g.fs.tf_from_data(data=data, ext=ext.ext, filename=filename, binary=binary)
                fp = tf.get_fingerprint()
                if fp in self.fingerprints:
                    pass
                else:
                    if self.board.file_min_size <= tf.size and tf.size <= self.board.file_max_size :
                        return self.add_file(tf, ext)
                    elif self.board.file_max_size < tf.size:
                        self.errors.append(_('%s: file is too big') % filename)
                    else:
                        self.errors.append(_('%s: file is too small') % filename)
            else:
                self.errors.append(_('%s: unknown file type') % filename)
        except Exception as e:
            log.info("Exception(): %s" % e)
            traceback.print_exc()
            self.errors.append('%s: exception - %s' % (filename, e))
        return None

    def add_from_image(self, image, filename, **kw):
        try:
            ext = g.extensions.exts['jpg']
            if ext:
                tf = g.fs.tf_from_image(image=image, ext=ext.ext, filename=filename, **kw)
                fp = tf.get_fingerprint()
                if fp in self.fingerprints:
                    pass
                else:
                    if self.board.file_min_size <= tf.size and tf.size <= self.board.file_max_size :
                        return self.add_file(tf, ext)
                    elif self.board.file_max_size < tf.size:
                        self.errors.append(_('%s: file is too big') % filename)
                    else:
                        self.errors.append(_('%s: file is too small') % filename)
            else:
                self.errors.append(_('%s: unknown file type') % filename)
        except Exception as e:
            log.info("Exception(): %s" % e)
            traceback.print_exc()
            self.errors.append('%s: exception - %s' % (filename, e))
        return None            

    def return_existing_file(self, f):
        if not f in self.fileset:
            self.fileset.append(f)
            for fp in f.fingerprints:
                fpt = fp.get_tuple()
                if not fpt in self.fingerprints:
                    self.fingerprints.append(fpt)
        return f
                

    def add_file(self, tf, ext):
        f2 = Fingerprint.get_file(type=ext.ext, quantifier=tf.size, fingerprint=tf.sha256)
        if f2:
            return self.return_existing_file(f2)
        else:
            fp1 = tf.get_fingerprint()
            fp2 = None
            tf2, fpl, errors = ext.filetype.preprocess(tf, ext, self.board)
            if errors:
                for err in errors:
                    self.errors.append(_('%s: %s') % (tf.filename_original, err))
                return None
            
            if fp1 != tf2.get_fingerprint():
                fpl.append(tf2.get_fingerprint())

            if fpl:
                for fp in fpl:
                    f2 = Fingerprint.get_file(type=fp[0], quantifier=fp[1], fingerprint=fp[2])
                    if f2:
                        Fingerprint(t=fp1, f=f2)
                        return self.return_existing_file(f2)
            if not fp1 in fpl:
                fpl.append(fp1)
            file = File(ext=g.extensions.exts[tf2.ext], temp_file=tf2, keep_filename=self.keep_filenames)
            file.process(self.board.thumbnail_resolution, fileset=self)
            if file.file_id:
                self.fileset.append(file)
                for fp in fpl:
                    Fingerprint(t=fp, f=file)
                    if not fp in self.fingerprints:
                        self.fingerprints.append(fp)
                return file                
            else:
                self.errors.append(_('%s: could not be processed') % tf.filename_original)
        return None
