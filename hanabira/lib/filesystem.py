# -*- coding: utf-8 -*-
import os, re, time, cgi, shutil, hashlib
from datetime import datetime
import logging
log = logging.getLogger(__name__)

hff_chars = ["\x00", "\n", "\r", " ", "!", "#", "$", "%", "&", ";", "'", '"', "`", "@", "*", "|", "\\", "?", '/', '<', '>']
hff_trim_re = re.compile("""(--+)""")
fff_re = re.compile("""-(\d+)$""")

vk_file_re = re.compile("^[xyzma]\_[a-z0-9]*$")

class FileSystem(object):
    settings = None
    localpath= None
    temppath = None
    def __init__(self, settings):
        self.settings = settings
        self.localpath= str(settings.path.static)
        self.temppath = str(settings.path.temp)
        if not os.path.exists(self.temppath):
            os.makedirs(self.temppath)

    def temp_file(self, filename):
        return os.path.join(self.temppath, filename)

    def new_temp_path(self, ext):
        name = str(int(time.time() * 10**5))
        return self.temp_file("%s.%s" % (name, ext))
    
    def local(self, filename):
        return os.path.join(self.localpath, filename)

    def web(self, path):
        return u"/%s" % path
    
    def filter_filename_orig(self, fn):
        fn, ext = fn.rsplit('.', 1)
        if vk_file_re.match(fn):
            fn = str(long(time.time() * 10**5))
        fn = self.hard_filter_filename(fn)
        return '.'.join((fn, ext))
    
    def make_filename(self, file, parent):
        ffn = file.filename.rsplit('.', 1)[0]
        #ffn = self.hard_filter_filename(ffn)
        ffn = self.find_free_file(self.local(parent), ffn, file.ext.ext)
        return ffn

    def filter_filename(self, filename):
        return filename.rsplit('\\', 1)[-1].rsplit('/', 1)[-1]

    def store_temp_file(self, fobj, ext, rating):
        return TempFile.from_fobj(fs=self, fobj=fobj, ext=ext, rating=rating)

    def new_tf(self, tempfile, path):
        return TempFile.from_tf(fs=self, tf=tempfile, filepath=path)

    def tf_from_file(self, f):
        return TempFile.from_file(fs=self, f=f)

    def tf_from_data(self, data, ext, filename, binary):
        return TempFile.from_data(fs=self, data=data, ext=ext, filename_original=filename, binary=binary)

    def tf_from_image(self, image, ext, filename, **kw):
        return TempFile.from_image(fs=self, image=image, ext=ext, filename_original=filename, **kw)

    def thumbnail(self, *args, **kw):
        return Thumbnail(*args, **kw)

    def hard_filter_filename(self, filename):
        hff = filename
        for ch in hff_chars:
            hff = hff.replace(ch, '-')
            hff = hff_trim_re.sub("-", hff)
        if len(hff) > 50:
            hff = hff[0:50]
        if hff[-1] == '-' and len(hff) > 1:
            hff = hff[:-1]
        return hff

    def find_suffix(self, name):
        match = fff_re.findall(name)
        if match:
            idx = int(match[0])
            cut = len(match[0]) + 1
            if len(name) > cut:
                name = name[:-cut]
            return (name, "-%s" % idx, idx)
        return None

    def find_free_file(self,path, name, ext):
        if not os.path.exists(path + name + '.' + ext):
            return name + '.' + ext
        match = fff_re.findall(name)
        if match:
            idx = int(match[0])
            cut = len(match[0]) + 1
            if len(name) > cut:
                name = name[:-cut]
        else:
            idx = 2
        while True:
            tn = "%s-%s.%s" % (name, idx, ext)
            if not os.path.exists(path + tn):
                return tn
            idx += 1

    def get_name(self, filepath):
        return self.filter_filename(filepath).split('.')[0]

    def get_ext(self, filepath):
        return self.filter_filename(filepath).split('.')[-1]


class TempFile(object):
    """
    This should be merged with File class. We have no need for separate temp class actually
    """
    fs = None
    sha256 = None
    @classmethod
    def from_file(cls, fs, f):
        return cls(fs=fs, date=f.date_added, rating=f.rating, path=fs.local(f.path), filename_original=f.filename)

    @classmethod
    def from_tf(cls, fs, tf, filepath):
        ntf = cls(fs=fs, date = tf.date, rating = tf.rating, path = filepath, filename_original = tf.filename_original)
        return ntf
    
    @classmethod
    def from_fobj(cls, fs, fobj, ext, date=None, rating=u'unrated'):
        name = str(int(time.time() * 10**5))
        filename = "%s.%s" % (name, ext)
        path = fs.temp_file(filename)
        if not date:
            date = datetime.now()
        f = open(path, 'w+b')
        if isinstance(fobj, cgi.FieldStorage):
            filename_original = fobj.filename
            shutil.copyfileobj(fobj.file, f)
            fobj.file.close()
            f.close()
        else:
            f.close()
            raise Exception("no data specified")
        return cls(fs=fs, date=date, rating=rating, path=path, filename_original=filename_original)
        
    @classmethod
    def from_data(cls, fs, data, ext, filename_original=None, date=None, rating=u'unrated', binary=False):
        name = str(long(time.time() * 10**5))
        filename = "%s.%s" % (name, ext)
        path = fs.temp_file(filename)
        if not date:
            date = datetime.now()
        if data:
            f = open(path, 'w+b')
            if binary:
                f.write(data)
            else:
                f.write(data.encode("utf8"))
            f.close()
        else:
            raise Exception("no data specified")
        return cls(fs=fs, date=date, rating=rating, path=path, filename_original=filename_original)

    @classmethod
    def from_image(cls, fs, image, ext, filename_original=None, date=None, rating=u'unrated'):
        name = str(long(time.time() * 10**5))
        filename = "%s.%s" % (name, ext)
        path = fs.temp_file(filename)
        if not date:
            date = datetime.now()
        image.write(path)
        return cls(fs=fs, date=date, rating=rating, path=path, filename_original=filename_original)
        
    def __init__(self, fs, date, rating, path, filename_original):
        self.fs = fs
        self.name = fs.get_name(path)
        self.filename = fs.filter_filename(path)
        self.ext = fs.get_ext(path)
        self.date = date or datetime.now()
        self.rating = rating or u'unrated'
        self.path = path
        self.filename_original = filename_original
        self.size = os.stat(self.path)[6]
        self.sha256 = hashlib.sha256(open(self.path, 'r+b').read()).hexdigest()

    def save(self, path):
        d = os.path.dirname(path)
        if not os.path.exists(d):
            os.makedirs(d)
        os.rename(self.path, path)

    def read(self, mode='r'):
        if hasattr(self, 'data'):
            return self.data
        else:
            open(self.path, mode).read()

    def write(self, data, mode='w', keep_data=False):
        self.sha256 = hashlib.sha256(data).hexdigest()
        f = open(self.path, mode)
        f.write(data)
        f.close()
        self.size = os.stat(self.path)[6]
        if keep_data:
            self.data = data
        else:
            if hasattr(self, 'data'):
                del self.data

    def get_sha256(self):
        return hashlib.sha256(self.read()).hexdigest()

    def get_fingerprint(self):
        return (self.ext, self.size, self.sha256)

    def change_ext(self, ext):
        self.ext = ext
        filepath = self.fs.new_temp_path(ext)
        self.name = self.fs.get_name(filepath)
        self.filename = self.fs.filter_filename(filepath)
        os.rename(self.path, filepath)
        self.path = filepath
    
class Thumbnail(TempFile):
    def __init__(self, path, ext, width, height):
        self.path = path
        self.ext = ext
        self.width = width
        self.height = height

