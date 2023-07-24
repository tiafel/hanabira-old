from urllib.parse import unquote, quote_plus

def process_google_url(uri):
    if (
        'q' in uri.query and 
        uri.location in ['/search', '/url', '/imglanding', '/m', '/imgres']
        ):    
        q = unquote(uri.query['q'])
        uri.href = uri.string
        uri.text = "google://" + q
        uri.search_query = q
        
def process_google_proto(uri):
    uri.proto = 'http'
    uri.href = ("http://google.com/search?q=" + 
                quote_plus(uri.location, '/+'))
    uri.text = uri.string
