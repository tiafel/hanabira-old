# -*- coding: utf-8 -*-
from sqlalchemy.sql import and_, or_, not_, func
import math
import logging
log = logging.getLogger(__name__)

def get_model_attr(model, attr):
    path = attr.split('.')
    m = model
    for el in path:
        m = m.__dict__[el]
    return m

class Filter(object):
    id = 0
    base = None
    filters = None
    sort = None
    filter = None
    page = None
    per_page = None
    pages = None
    total = None
    restrictions = None
    def __init__(self, base=None, per_page=10, sort=None, filters=None, restrictions=None):
        self.base = base
        self.per_page = per_page
        if not sort:
            sort = []
        if not filters:
            filters = []
        self.filters = filters
        self.restrictions = restrictions
        self.sort = sort
        filter = self.compile_filter()
        self.total = filter.count()
        self.pages = int(math.ceil(float(self.total)/self.per_page))

    def compile_filter(self):
        model = self.base.model
        if self.base.query:
            q = model.__dict__[self.base.query]
            if type(q) == classmethod:
                filter = q.__get__(None, model)()
            else:
                filter = q()
        else:
            filter = model.query
        # Apply filters
        for f in self.filters:
            filter = filter.filter(self.base.filters[f[0]][0].__dict__[f[0]] == f[1])
        # Apply sorting
        for s in self.sort:
            filter = filter.order_by(self.base.sort[s[0]].__dict__[s[0]].__getattr__(s[1])())
        return filter        

    def get(self, page=0):
        self.page = page
        filter = self.compile_filter()
        return filter.offset(self.page * self.per_page).limit(self.per_page).all()
        

class FilterBase(object):
    filters = None
    sort = None
    model = None
    query = None
    default_sort = None
    default_filters = None
    default_per_page = None
    restrictions = None
    def __init__(self, model=None, filters=None, sort=None, query=None, default_sort=None, default_per_page=10, default_filters=None, restrictions=None):
        self.model = model
        self.filters = filters
        for s in sort:
            if not sort[s]:
                sort[s] = model
        self.sort = sort
        self.query = query
        self.default_sort = default_sort or []
        self.default_per_page = default_per_page
        self.default_filters = default_filters or []
        self.restrictions = restrictions

    def filter(self, params, restrictions=None):
        per_page = int(params.get('per_page', self.default_per_page))
        sort = []
        filters = []
        if params.__class__ != dict:
            raw_sort = params.getall('sort')
            if raw_sort:
                for rs in raw_sort:
                    rs2 = rs.split(':', 1)
                    if rs2[0] in self.sort and rs2[1] in ['asc', 'desc']:
                        sort.append((rs2[0], rs2[1]))
            for rf in params.getall('filter'):
                rf2 = rf.split(':', 1)
                if rf2[0] in self.filters:
                    filters.append((rf2[0], rf2[1]))
        else:
            sort = self.default_sort
            filters = self.default_filters
        return Filter(base=self, per_page=per_page, sort=sort, filters=filters, restrictions=restrictions)


class Filters(object):
    filters = None
    def __init__(self):
        self.filters = [None]

    def save(self, filter):
        i = len(self.filters)
        self.filters.append(filter)
        filter.id = i
        return i

    def get(self, i, base):
        return self.filters[i]

    def handle(self, base, post, filter_id):
        filter_id = filter_id and int(filter_id) or 0
        if post:
            filter = base.filter(post)
            filter_id = self.save(filter)
        elif filter_id:
            filter = self.get(filter_id, base)
        else:
            filter = base.filter({})
        return filter
        
