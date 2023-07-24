# -*- coding: utf-8 -*-
from pylons import request, response, session, tmpl_context as c, app_globals as g
from pylons.templating import render_mako
from datetime import datetime
import logging
from functools import reduce
trace_log = logging.getLogger('trace')

class FuncTracer(object):
    def __init__(self):
        self.funcs = []
        self.stack = []
        self.times = {}
        self.first = None
        self.last  = None
        self._header = None
        
    def trace(self, name):
        now = datetime.now()        
        if name in self.times:
            if self.times[name][1] != None:
                return None
                #raise Exception("Call for {0} was already traced!".format(name))
            name2 = self.stack.pop()
            while name != name2 and name2:
                self.times[name2][1] = now
                name2 = self.stack.pop()
            self.times[name][1] = now
            self.last = now
        else:
            self.funcs.append(name)
            self.stack.append(name)
            self.times[name] = [now, None]
            if not self.first:
                self.first = now
                
    def print_times(self):
        over_limit = False
        ct = self.last - self.first
        ct = ct.seconds + float(ct.microseconds)/1000000
        if ct >= float(str(g.settings.trace.time_limit)):
            over_limit=True
            
        if not (over_limit or str(g.settings.trace.time_show_all) == 'true'):
            return 
        
        msg = [self.header]
        maxlen = len(reduce(lambda x,y:len(x) > len(y) and x or y, self.funcs))
        for name in self.funcs:
            vals = self.times[name]
            if vals[1]:
                diff = vals[1] - vals[0]
                msg.append("\t{0} : {1}".format(name.ljust(maxlen, ' '), diff))
        if over_limit:
            trace_log.error("\n".join(msg))
        else:
            trace_log.info("\n".join(msg))
            
    @property
    def header(self):
        if self._header:
            return self._header
        route = request.environ['pylons.routes_dict']
        sess = ''
        if session.is_bot:
            sess = ' BOT'
        elif session.is_new:
            sess = ' NEW'
        act   = "{0[controller]}.{0[action]}({2}) from {1.ip} {1.country}{3}".\
            format(route, request, 
                   request.environ['PATH_INFO'],
                   sess
                   )
        self._header = act
        return act

def trace_time(name):
    if str(g.settings.trace.enabled) == 'true':
        tracer = c.tracer
        if not tracer:
            tracer = FuncTracer()
            c.tracer = tracer
        tracer.trace(name)
        
def render(template, *args, **kw):
    trace_time('render')
    res = render_mako(template, *args, **kw)
    trace_time('render')
    return res
