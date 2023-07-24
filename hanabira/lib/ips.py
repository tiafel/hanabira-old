# -*- coding: utf-8 -*-

import logging

log = logging.getLogger(__name__)

class IP(object):
    def __init__(self, ip):
        if ip:
            self.int = self.get_int(ip)
            self.str = str(self)
        else:
            self.int = 0

    def __nonzero__(self):
        return bool(self.int)

    def __repr__(self):
        return "<IP('{0}')>".format(str(self))

    def __str__(self):
        return "{0}.{1}.{2}.{3}".format(
            (self.int >> 24) & 0xff,
            (self.int >> 16) & 0xff,
            (self.int >> 8) & 0xff,
            self.int & 0xff)
    
    def get_int(self, ip):
        if isinstance(ip, IP):
            return ip.int
        if isinstance(ip, str):
            if not "." in ip:
                return int(ip)
            else:
                ip = list(map(lambda x: int(x), ip.split('.')))
                return (ip[0] << 24) + (ip[1] << 16) + (ip[2] << 8) + ip[3]
        else:
            if isinstance(ip, int):
                return ip
            else:
                return int(ip)
    
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

