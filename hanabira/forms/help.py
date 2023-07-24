from pylons.i18n import _, ungettext, N_
from hanabira.forms import *
from hanabira.model import meta
from hanabira.model.help import HelpArticle
from formalchemy.fields import Field

import logging
log = logging.getLogger(__name__)

def HelpArticleForm(article=HelpArticle):
    session = None
    if article == HelpArticle:
        session = meta.Session    
    fs = FieldSet(article, session=session)
    fs.configure(options=[fs.text_raw.textarea("60x10"), 
                          fs.markup.dropdown(options=["wakabamark", "reStructuredText"])],
                 exclude=[fs.text])
    return fs
