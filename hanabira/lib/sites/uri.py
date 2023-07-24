class URI(object):
    proto = None
    is_local = False
    location = None
    query = None
    string = None
    href = None
    text = None
    
    def __init__(self, url):
        self.string = url
        self.query = {}
        self.proto, location = url.split(':', 1)
        if location.startswith('//'):
            location = location[2:]
        query = None
        if '?' in location:
            location, query = location.split('?', 1)
        self.location = location
        if query:
            for param in query.split('&'):
                if '=' in param:
                    key, value = param.split('=', 1)
                    self.query[key.lower()] = value
                    
    def get_href(self):
        return self.href
    
    def get_text(self):
        return self.text