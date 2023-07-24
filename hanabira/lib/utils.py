from pylons.i18n import _, ungettext, N_
import re
import os
import chardet
import subprocess
import traceback
import random
import inspect
import logging
import time
log = logging.getLogger(__name__)

int_re = re.compile("""^[-+]?[0-9]+$""")
def is_int(n):
    if isinstance(n, int):
        return True
    if n and isinstance(n, str):
        if re.match("^[-+]?[0-9]+$", n):
            return True
        else:
            return False
    else:
        return False

def safe_int(n):
    if is_int(n):
        return int(n)
 
def unreadable_char(c):
    o = ord(c)
    return is_smp(o) and not utf_trash(o)

def is_smp(o):
    return o < 55296 or (57343 < o and o < 65535)

utf_trash_set = set([8206, 8207, 8238, 8234, 8235, 8237, 8236, 8203, 8204, 8205])

def utf_trash(o):
    return o in utf_trash_set or (746 < o < 883) or (1159 < o < 1167)

def sanitized_unicode(text):
    if type(text) == str:
        return ''.join(list(filter(unreadable_char, text))).strip()
    else:
        return ""

def add_error(errors, t, e):
    if not t in errors:
        errors[t] = [e]
    else:
        errors[t].append(e)

good_chars = [235, 246, 252]
bad_charsets = ['ISO-8859-2']
try_charsets = ['Shift-JIS', 'windows-1251']
def fix_charset(text):
    if type(text) == str:
        try:
            res = str(text, 'utf-8')
        except Exception:
            try:
                enc = chardet.detect(text)
                res = str(text, enc['encoding'])
            except Exception:
                raise Exception(_("unknown charset"))
        return res
    elif type(text) == str:
        return text
    else:
        raise Exception("should be either str or unicode, got %s" % type(text))

def fix_charset_unicode(text, encoding=None):
    if type(text) == str:
        if encoding and encoding == 'utf-8':
            return (text, 'utf-8')
        bad_chars = 0
        strl = []
        for c in text:
            o = ord(c)
            if o > 255:
                return (text, 'utf-8')
            elif o > 127 and not o in good_chars:
                bad_chars += 1
            strl.append(chr(o))
        textl = ''.join(strl)
        if encoding:
            try:
                return str(textl, encoding), encoding
            except Exception:
                return text, None
        elif bad_chars:
            enc = chardet.detect(textl)
            encodings = []
            if not enc['encoding']:
                encodings = try_charsets
            elif enc['encoding'] in bad_charsets:
                encodings = try_charsets + [enc['encoding']]
            else:
                encodings = [enc['encoding']] + try_charsets
            for et in encodings:
                try:
                    res = str(textl, et)
                    return res, et
                except Exception:
                    pass
            return text, None
        return text, None
    else:
        raise Exception("should be unicode")
        
def popen(command, raise_errors=False):
    if raise_errors:
        sp = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        e = sp.stderr.read()
        if e: raise Exception(_("%s returned error:\n%s") % (command.split(' ')[0], e))
        r = sp.stdout.read()
    else:
        r = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE).stdout.read()
    return r.decode('utf-8')

def ipToInt(ipstr):
    if type(ipstr) == int: return ipstr
    ip = [int(x) for x in ipstr.split('.')]
    return (ip[0] << 24) + (ip[1] << 16) + (ip[2] << 8) + ip[3]
    
def intToIp(ip):
    if type(ip) in [str, str]: return ip
    return "%s.%s.%s.%s"%((ip >> 24) & 0xff, (ip >> 16) & 0xff, (ip >> 8) & 0xff, ip & 0xff)
    
def whois(ip, ww=None, html=None):
    ip = intToIp(ip)
    if ww:
        r = popen("whois %s"%ip)
    else:
        r = popen("whois -h whois.ripe.net -p 43 -B -T inetnum,organisation %s"%ip)
    rereq = 0
    res = []
    for line in r.split('\n'):
        if line.find('inetnum') == 0:
            range = line.rsplit('  ',1)
            if len(range) == 1: range = line.rsplit('\t',1)
            range = range[1]
            if range == '0.0.0.0 - 255.255.255.255' and not ww:
                rereq = 1
                break
            else:
                mask = implicitMask(range.split(' - '))
                res.append('%s%s'%(range, mask and ' (mask %s)'%mask or ''))
        if line.find('descr') == 0 or line.find('address') == 0 or line.find('netname') == 0:
            string = line.rsplit('  ',1)
            if len(string) == 1: string = line.rsplit('\t',1)
            res.append(string[1])
    if rereq:
        return whois(ip, 1)
    else:
        res = '\n'.join(res)
        if html:
            return '%s\n<input id="subnet" type="hidden" value="%s"/>'%(res, range)
        else:
            return res
        
def implicitMask(rng):
    f = ipToInt(rng[0])
    l = ipToInt(rng[1])
    i = 0
    for i in range(12,32)[::-1]:
        lm = mask_ip(l, i)
        if mask_ip(f, i) == lm and mask_ip((l+1), i) != lm: break
        i = 0
    return i
    
def mask_ip(ip, val):
    if val < 0:
        maskv = 32+val
    else:
        maskv = val
        val = 32 - val
    return ip - (ip & 2**val - 1)

def log_caller():
    s = inspect.stack()
    log.info("%s called from (%s):%s from function %s()" % (s[1][3], s[2][1], s[2][2], s[2][3]))
    
def log_line(text=''):
    s = inspect.stack()
    log.info("line %s function %s: %s"%(s[1][2], s[1][3], text))
    
def timer(times, method):
    t0 = time.time()
    for i in range(times):
        method()
    print(("%.3f ms"%(time.time() - t0)*1000/times))
    
class LW(object):
    def __init__(self, d):
        self.dict = d
    def __getitem__(self, name):
        return self.dict.get(name, '')
    def __contains__(self, name):
        return True
        
ib_url_re = re.compile(r'https?://([^/]+)/([^/]+)/((\d+)|res/(\d+)|\w+)(\.x?html)?(#i?(\d+))?')
def parse_url(url):
    m = re.search(ib_url_re, url)
    if m:
        return {'chan'   : m.group(1),
                    'board' : m.group(2),
                    'page'   : m.group(4),
                    'thread': m.group(5),
                    'post'   : m.group(8) }
    else:
        return {}
        
def break_to_lines(text, maxlen, no_blanks=False):
    if maxlen < 1:
        raise Exception("Can't break text with maxlen = %s"%maxlen)
    lines = []
    for string in text.split('\n'):
        string = string.strip()
        if len(string) <= maxlen:
            lines.append(string)
            continue
        words = re.split(r'\s+', string)[::-1]
        buf = None
        while words or buf:
            lines.append('')
            if buf:
                lines[-1] += buf
                buf = None
            while words:
                buf = '%s '%words.pop()
                if len(lines[-1]) + len(buf) - 1 > maxlen:
                    break
                lines[-1] += buf
                buf = None
    lines = list(map(str.strip, lines))
    if no_blanks:
        return '\n'.join(filter(bool, lines))
    else:
        return '\n'.join(lines)
