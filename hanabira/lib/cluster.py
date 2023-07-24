from pylons import url, app_globals as g
import requests

import logging
log = logging.getLogger(__name__)

def reload_nodes():
    for node in g.slave_nodes:
        if node:
            requests.get("http://{node}{url}".format(node=node,
                                                     url=url('reload')))
    
        
    
