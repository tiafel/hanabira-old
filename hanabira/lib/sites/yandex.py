from urllib.parse import unquote, quote_plus

def process_yandex_url(uri):
    if (
        'text' in uri.query
        ):
        q = unquote(uri.query['text'])
        uri.href = uri.string
        uri.text = "yandex://" + q
        uri.search_query = q
        
def process_yandex_proto(uri):
    uri.proto = 'http'
    uri.href = ("http://yandex.ru/yandsearch?text=" + 
                quote_plus(uri.location.encode('utf-8'), '/+'))
    uri.text = uri.string
