# -*- coding: utf-8 -*-
from pylons import app_globals as g

from .local import process_help
from .youtube import process_youtube
from .google import process_google_url, process_google_proto
from .yandex import process_yandex_proto, process_yandex_url
from .wiki import process_wiki_proto, process_wiki_url
from .mal import process_mal_proto, process_mal_url
from .uri import URI
    
def process_http(uri, ext=True):
    if '/' in uri.location:
        uri.domain, uri.location = uri.location.split('/', 1)
        if not uri.location or uri.location[0] != '/':
            uri.location = "/" + uri.location
    else:
        uri.domain = uri.location
        uri.location = '/'
    
    if uri.domain in g.local_domains:
        pass
    
    elif 'wikipedia.org' in uri.domain or 'lurkmore.ru' in uri.domain:
        process_wiki_url(uri)
    
    elif 'google' in uri.domain:
        process_google_url(uri)
        uri.domain = 'google'
    
    elif ('youtube' in uri.domain or 'youtu.be' in uri.domain) and ext:
        process_youtube(uri)
    
    elif 'yandex' in uri.domain:
        process_yandex_url(uri)
        uri.domain = 'yandex'
        
    elif 'myanimelist' in uri.domain:
        process_mal_url(uri)
    
    if uri.text is None:
        process_plain(uri)
        
    if len(uri.text) > 80:
        uri.text = uri.text[0:70] + '[...]' + uri.text[-5:]

def process_plain(uri):
    uri.href = uri.string
    uri.text = uri.string

proto_map = dict(http  = process_http,
                 https = process_http,
                 
                 #magnet
                 
                 lm = process_wiki_proto,
                 wiki = process_wiki_proto,
                 ruwiki = process_wiki_proto,
                 enwiki = process_wiki_proto,
                 help = process_help,
                 google = process_google_proto,
                 yandex = process_yandex_proto,
                 mal = process_mal_proto,
                 )

def parse_uri(uri):
    uri = URI(uri)
    
    if uri.proto in proto_map:
        proto_map[uri.proto](uri)
    else:
        process_plain(uri)
        
    return uri
    
