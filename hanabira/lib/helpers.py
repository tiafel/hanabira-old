# -*- coding: utf-8 -*-
"""
Helper functions
"""
import datetime, time
import os
import string
import re
import hashlib
from crypt import crypt

from pylons import config, url, app_globals as g, tmpl_context as c
from pylons.i18n import _, ungettext, N_
from webhelpers import *
from pytils import dt

from hanabira.lib.utils import *

salt_trans = str.maketrans(":;<=>?@[\\]^_`", "ABCDEFGabcdef")
ratings = ['sfw','r-15','r-18','r-18g','illegal']
#md4 = hashlib.new('md4')

import logging
log = logging.getLogger(__name__)

def ugt(singular, plural, qty):
    return ungettext(singular, plural, qty)%qty

def acceptable_censorship(file, rating, rating_strict=True):
    if file.rating not in ratings:
        return not rating_strict
    else:
        return ratings.index(rating) >= ratings.index(file.rating)
    
def postUrl(board, thread, post):
    return '%s#i%s' % (url('thread', board=board, thread_id= thread or post), post)
    
def reflink(board, thread_id, post, reply):
    str = 'href="%s"'%postUrl(board, thread_id, post.display_id)
    if reply and not post.op:  
        str = '%s onclick="Highlight(0, %s)"'%(str, post.display_id)
    return str
    
def filepan(files, this_id):
    str = '''onmousedown="get_filepan(event, %s, '%s'''%(this_id, files[0].id)
    for f in files[1:]:
        str = '%s_%s'%(str, f.id)
    return '''%s')"'''%str
    
def userpan(post, thread):
    invis = post.op and thread.invisible or post.invisible
    return ''' onmousedown="get_userpan(event, {0.id}, {1.id}, '{0.session_id}', {2:g}, {0.deleted:g})"'''.format(post, thread, invis)
    
def geoip(geoip):
    return '''<img class="geoicon" src="/images/geo/%s.png" alt="%s" title="%s" />'''%(geoip.lower(), geoip, g.country_codes.get(geoip, ''))
    
def whois_link(ip):
    return """<a onmouseover="whois(event, %s)">%s</a>"""%(ip, intToIp(ip))

def has_shorted(context, post):
    return not context.reply and post.message_short

def expandName(name):
    #log.debug("expanding: %s" % name)
    if name:
        parts = name.split('.')
        if parts and utils.isNumber(parts[-2].replace('s', '')): #TODO: is the second condition really needed?
            ext = parts[-1].lower()
            prefix = name[0:4]
            #log.debug('%s/%s/%s' % (ext, prefix, name))
            return '%s/%s/%s' % (ext, prefix, name)
    #log.debug('passed: %s' % name)
    return name


def filepath(filename):
    return filename


def temp_file(filename):
    return "%s%s" % (g.settings.path.temp, filename)

def static_local(filename):
    return "%s%s" % (g.settings.path.static, filename)

def static(filename):
    return "%s%s" % (g.settings.path.static_web, filename)

def static_domain(filename):
    url = "http://{0}{1}{2}".format(c.channel.host, g.settings.path.static_web, filename)
    return url

def static_versioned(filename):
    name, ext = filename.rsplit('.', 1)
    return "%s%s-%s.%s" % (g.settings.path.static_web, name, g.settings.dist.version, ext)

def board_name(board_id):
    if not board_id:
        return _('Global')
    else:
        if board_id in g.boards.board_ids:
            return g.boards.board_ids[board_id].title
        else:
            return _('Error')

def show_time(time, ctxt, timestamp=False):
    if timestamp:
        time = datetime.datetime.fromtimestamp(time)
    tf = str(ctxt.mini and g.settings.chan.mini_timeformat or g.settings.chan.timeformat)
    if 'ru' in ctxt.lang:
        return dt.ru_strftime(tf, inflected=True, date=time)
    else:
        return time.strftime(tf)


def wrap_with_a(text, cond, href=''):
    if not text:
        text = ''
    if cond:
        href = href or text
        return "<a href='%s'>%s</a>" % (href, text)
    else:
        return text
        
def button(klass, title=None, onclick=None, href=None, alt=None, insert='', double=False, new_tab=False):
    str = '<a class="%s icon"'%klass
    if onclick: str = '%s onclick="%s"'%(str, onclick)
    elif new_tab: str += ' onclick="' + "window.open(this.href,'_blank');return false;" + '" '
    if href: str = '%s href="%s"'%(str, href)
    str = '%s>%s<img src="/images/blank'%(str, insert)
    if double:
        str = '%s-double.png" style="vertical-align:sub"'%str
    else:
        str = '%s.png"'%str
    if title:
        alt = alt or title
        str = '%s title="%s"'%(str, _(title))
    if alt: str = '%s alt="%s"'%(str, _(alt))
    return '%s /></a>'%str

def tripcode(tc):
    if tc:
        code_parts = tc.split("!")
        code = code_parts[-1]
        salt = (code + "H.")[1:3].translate(salt_trans)
        crypted = crypt(code, salt)
        if not crypted:
            return ""
        return ("!" * (len(code_parts) - 1)) + crypt(code, salt)[-10:]
    else:
        return ""

def show_errors(field):
    if c.errors and field in c.errors:
        errstr=[]
        for error in c.errors[field]:
            errstr.append("<tr><td colspan='2' class='post-error'>%s</td></tr>" % error)
        return "\n".join(errstr)
    else:
        return ''
def input_value(value):
    if value is None:
        value = ''
    return "value='%s'" % value

def input_checkbox(value):
    if value:
        return "checked='checked'"
    else:
        return ''
    
def post_name(board, ctx):
    if ctx.post:
        if ctx.post.name is None:
            ctx.post.name = ''
        if ctx.post.tripcode is None:
            ctx.post.tripcode = ''
        return ctx.post.name + ctx.post.tripcode
    else:
        if board.remember_name:
            return ctx.username.get(board.board, board.default_name)
        else:
            return board.default_name
        
def post_value(field):
    if c.post:
        return c.post.__getattribute__(field)
    else:
        return ''
    
def post_message():
    if c.post:
        return c.post.message_raw
    else:
        return ''    
def post_sage():
    if c.post:
        return input_checkbox(c.post.sage)
    else:
        return ''    


def cut_filename(filename):
    limit = int(str(g.settings.post.filename_limit))
    if len(filename) > limit:
        spt = filename.rsplit('.',1)
        if len(spt) > 1:
            name, ext = spt
        else:
            name = filename
        return name[0:(limit - 3)] + '...'
    else:
        return filename
        
def get_ext(filename):
    ext = filename.rsplit('.',1)[1]
    if ext:
        return ext
    else:
        return ''

def now():
    return str(int(time.time()*1000))
  
def make_ip_hash(thread_id, session_id):
    md5 = hashlib.md5(str(thread_id).encode('utf-8') + session_id.encode('utf-8')).hexdigest().upper()
    marks = []
    for color in  [md5[x*6:x*6+6] for x in range(5)]:
        marks.append("<span class='ipmark' style='background: #%s;'>&nbsp;</span>" % color)
    return ''.join(marks)
    
