from pylons.i18n import _, ungettext, N_
from hanabira.forms import *
from hanabira.model import meta
from hanabira.model.boards import Board, Section
from formalchemy.fields import Field

import logging
log = logging.getLogger(__name__)

def SectionForm(section=Section):
    session = None
    if section == Section:
        session = meta.Session    
    return FieldSet(section, session=session)

def BoardForm(board=Board, filetypes=[]):
    session = None
    if board == Board:
        session = meta.Session
    fs = FieldSet(board, session=session)
    #fs.add(Field('filetypes', value=fts).label(_("Allowed file types")))
    # Dirty hack inside FA sources!!!
    fs.allowed_filetypes.is_list = True
    fs.allowed_new_files.is_list = True
    fs.configure(options=[fs.allowed_filetypes.dropdown(options=filetypes, multiple=True, size=10), fs.allowed_new_files.dropdown(options=filetypes, multiple=True, size=10)],
                 exclude=[fs.post_index, fs.thread_index, fs.posts, fs.threads])
    return fs
