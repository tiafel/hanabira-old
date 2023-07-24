from urllib.parse import unquote, quote_plus

domains = {'lurkmore.ru': 'lm',
           'en.wikipedia.org': 'enwiki',
           'ru.wikipedia.org': 'ruwiki'}

wikis = {'lm': 'http://lurkmore.ru/index.php?title=Служебная%3ASearch&search=',
         'enwiki': 'http://en.wikipedia.org/w/index.php?title=Special:Search&search=',
         'ruwiki': 'http://ru.wikipedia.org/w/index.php?title=Special:Search&search=',
         'wiki': 'http://ru.wikipedia.org/w/index.php?title=Special:Search&search='}

def process_wiki_url(uri):
    proto = domains.get(uri.domain, '')
    if proto:
        page = None
        if not uri.query:
            page = uri.location.rsplit('/', 1)[-1]
        elif 'search' in uri.query:
            page = uri.query['search']
        if page:
            uri.text = proto + "://" + unquote(page.encode('utf-8')).decode('utf-8')
            uri.href = uri.string
            
def process_wiki_proto(uri):
    url_base = wikis.get(uri.proto, '')
    if url_base:
        uri.text = uri.string
        uri.href = url_base + quote_plus(uri.location.encode('utf-8'), '/+')