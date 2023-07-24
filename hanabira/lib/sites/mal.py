from urllib.parse import unquote, quote_plus

import logging
log = logging.getLogger(__name__)

def process_mal_url(uri):
    location_parts = uri.location.split('/', 3)
    if len(location_parts) > 3 and location_parts[1] == 'anime':
        title = unquote(location_parts[3].encode('utf-8')).decode('utf-8')
        uri.href = uri.string
        uri.text = "mal://" + title
        
def process_mal_proto(uri):
    uri.proto = 'http'
    uri.href = ("http://myanimelist.net/anime.php?q=" + 
                quote_plus(uri.location.encode('utf-8'), '/+'))
    uri.text = uri.string