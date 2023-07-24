# -*- coding: utf-8 -*-

from .files import File
from .fileset import FileSet
from .filetype import Filetype
from .images import ImageFile, VectorFile
from .music import MusicFile
from .archive import ArchiveFile
from .flash import FlashFile
from .pdf import PDFFile
from .text import TextFile, CodeFile
from .fingerprints import Fingerprint
from .extensions import Extension, Extensions
from .ratings import ratings

import logging
log = logging.getLogger(__name__)

