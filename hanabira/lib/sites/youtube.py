# -*- coding: utf-8 -*-
import logging
log = logging.getLogger(__name__)

# http://youtu.be/Y4WlHeNJ9_k 

def process_youtube(uri):
    v_key = None
    if uri.location == "/watch" and 'v' in uri.query:
        v_key = uri.query['v']
    elif uri.domain == 'youtu.be' and len(uri.location) > 2:
        v_key = uri.location[1:]
    
    if v_key:
        if '#' in v_key:
            v_key = v_key.split('#')[0]
        req_url = ("http://gdata.youtube.com/feeds/api/"
                   "videos/{0}?v=2&alt=jsonc".format(v_key))
        
        resp = client.request(req_url)
        data = resp.json
        if 'data' in data:
            uri.href = "http://www.youtube.com/watch?v={0}".format(v_key)
            uri.text = "YouTube: " + data.data.title
