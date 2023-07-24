# -*- coding: utf-8 -*-

#from difflib import HtmlDiff
#from htmltreediff import diff
from htmldiff import render_html_diff

from .base import *

import logging
log = logging.getLogger(__name__)

class PostRevisionsView(BaseView):
    def __init__(self, post, revisions):
        self.post = post
        self.revisions = revisions
        
    def make_diff(self, revision1, revision2):
        ## difflib
        #htmldiff = HtmlDiff()
        #from_l = revision2.message_raw.split("\n")
        #to_l = revision1.message_raw.split("\n")
        #return htmldiff.make_table(from_l, to_l)
        
        ## htmltreediff
        #return diff(revision2.message_html, revision1.message_html)
        
        return render_html_diff(revision2.message_html, revision1.message_html)
    
    def make_xhtml(self):
        revisions = []
        i = 0
        l = len(self.revisions)
        for revision in reversed(self.revisions):

            j = l - i
            revision.index = j
            if (j - 2) >= 0:
                revision.diff = self.make_diff(revision, self.revisions[j-2])
                
            revisions.append(revision)
            i += 1
        
        c.post = self.post
        c.revisions = revisions
        return render('/utils/post_history.mako')
        