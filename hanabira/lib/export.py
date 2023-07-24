# -*- coding: utf-8 -*-
import json
import simplejson
import xml.etree.ElementTree as etree
import inspect

from pylons import (tmpl_context as c, app_globals as g,
                    cache, config, request, response, session, url)
from pylons.i18n import _, ungettext, N_

from hanabira.lib.decorators import make_args_for_spec
from hanabira.lib.trace import render

import logging
log = logging.getLogger(__name__)

error_codes = {
    # 404xx - does not exit
    40401:(40401, 'element_not_found', N_('Specified element does not exist.')),
    40420:(40420, 'element_deleted', N_('Specified element is deleted.')),    
    40421:(40421, 'post_deleted', N_('Post is deleted.')),
    40422:(40422, 'thread_deleted', N_('Thread is deleted.')),    
    

    # 403xx - permissions error
    # 4030x - read permission error
    40300:(40300, 'forbidden',
           N_('Current session does not have permissions to execute this request')),
    40301:(40301, 'element_read_not_allowed',
           N_('Current session does not have access to specified element.')),
    40302:(40302, 'board_read_not_allowed',
           N_('Current session does not have access to specified board.')),
    # 4035x - modify permission error
    40351:(40351, 'element_modify_not_allowed',
             N_('Current session does not have permissions to edit specified element')),
    }
error_aliases = {}
for err in error_codes.values():
    error_aliases[err[1]] = err

class HanabiraJSONEncoder(json.JSONEncoder):
    __ctxt = None
    def __init__(self, ctxt=None):
        json.JSONEncoder.__init__(self)
        if not ctxt:
            ctxt = {}
        self.__ctxt = ctxt
    def default(self, o):
        if hasattr(o, 'export_dict'):
            d = o.export_dict(**self.__ctxt)
            if not '__class__' in d:
                d['__class__'] = o.__class__.__name__
            return d
        else:
            return json.JSONEncoder.default(self, o)

def export_json(obj, ctxt=None):
    if hasattr(obj, '_current_obj'):
        obj = obj._current_obj()
    encoder = HanabiraJSONEncoder(ctxt)
    return encoder.encode(obj)

def api_ok(d=None):
    return {'status':'OK', 'result':True}

def export_result(r, format, func=None):
    opts = r['opts']
    del r['opts']
    if format in ['json', 'js']:
        # TODO: resolve context        
        response.headers['Content-Type'] = 'application/json'
        return export_json(r)
    elif format in ['xhtml']:
        template = opts.get('template', '')
        template_args = opts.get('template_args', [])
        if not template:
            log.warn("XHTML format without template, {0}".format(func))
            return "Cannot render this call result into XHTML"
        return render(template, *template_args)
    else:
        log.warn("Unknown format {0} for fn {1}".format(format, func))
        return r

def export(func):
    spec = inspect.getargspec(func)
    def export_decorator(self, **kw):
        format = kw.get('format', '')
        if not format:
            log.warn("Call without format! Fn: {0}".format(func))
        args = make_args_for_spec(spec, kw)
        r = func(self, **args)
        return export_result(r, format, func)
    
    return export_decorator

def result(r, **kw):
    return dict(
        result=r,
        error=None,
        opts=kw
        )

def error(c, m="", a="", **kw):
    if c in error_codes:
        et = error_codes[c]
    elif c in error_aliases:
        et = error_aliases[c]
    else:
        et = (c, a, m)
    return dict(
        result=None,
        error=dict(
            code=et[0],
            alias=et[1],
            message=_(et[2]),
            ),
        opts=kw
        )

def ExportJSON(threads=None, events=None, admin=None, board=None, page=None, pages=None, response=None):
    #log.warn("Used old export!")
    res = {'boards':{}, 'events':[]}
    if events:
        for event in events:
            res['events'].append(event.export())
    if board:
        res['boards'][board.board] = {'threads':[], 'capabilities':board.get_capabilities()}
        bd = res['boards'][board.board]
        if page:
            bd['page'] = page
        if pages:
            bd['pages'] = pages
            
    for thread in threads:
        b = thread.get_board()
        if not b.board in res['boards']:
            res['boards'][b.board] = {'threads':[], 'capabilities':b.get_capabilities()}
        res['boards'][b.board]['threads'].append(thread.export_dict(admin=admin))
    response.headers['Content-Type'] = 'application/json'
    return simplejson.dumps(res)

def ExportDict(parent, name, d):
    if parent is None:
        node = etree.Element(name)
    else:
        node = etree.SubElement(parent, name)
    contains = []
    for k in d:
        if type(d[k]) == dict or type(d[k]) == list:
            contains.append((k, d[k]))
        else:
            etree.SubElement(node, k).text = str(d[k])
    for k,v in contains:
        if type(v) == dict:
            ExportDict(node, k, v)
        else:
            ExportList(node, k, v)
    return node
def ExportList(parent, name, l):
    for v in l:
        if type(v) == dict:
            ExportDict(parent, name, v)
        elif type(v) == list:
            ExportList(parent, name, v)
        else:
            etree.SubElement(parent, name).text = str(v)

def ExportXML(threads=None, events=None, admin=None, board=None, page=None, pages=None, response=None):
    res = {'boards':{}, 'events':[]}
    if events:
        for event in events:
            res['events'].append(event.export())
    if board:
        res['boards'][board.board] = {'threads':[], 'capabilities':board.get_capabilities()}
        bd = res['boards'][board.board]
        if page:
            bd['page'] = page
        if pages:
            bd['pages'] = pages
            
    for thread in threads:
        b = thread.get_board()
        if not b.board in res['boards']:
            res['boards'][b.board] = {'threads':[], 'capabilities':b.get_capabilities()}
        res['boards'][b.board]['threads'].append(thread.export_dict(admin=admin))

    response.headers['Content-Type'] = 'application/xml'
    tree = ExportDict(None, "result", res)
    return etree.tostring(tree, xml_declaration=True, pretty_print=True, encoding='UTF-8')

def ExportAtom(threads=None, events=None, admin=None, board=None):
    return "Stub"

def ExportRSS(threads=None, admin=None, board=None):
    return "Stub"

def ExportRST(threads=None, admin=None, board=None):
    return "Stub"

def ExportText(threads=None, admin=None, board=None):
    return "Stub"

def Export(format='js', **kw):
    #log.warn("Used old export!")
    if format in ['js', 'json']:
        return ExportJSON(**kw)
    elif format in ['xml']:
        return ExportXML(**kw)
    elif format in ['rss', 'rdf']:
        return ExportRSS(**kw)
    elif format in ['atom']:
        return ExportAtom(**kw)
    elif format in ['rst']:
        return ExportRST(**kw)
    elif format in ['txt', 'text']:
        return ExportText(**kw)
    else:
        return "Unknown format"
