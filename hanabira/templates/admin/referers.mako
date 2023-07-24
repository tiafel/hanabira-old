# -*- coding: utf-8 -*-
<%inherit file="admin.mako" />
<%include file="filter.mako" args="filter=c.filter" />
<%include file="filter.paging.mako" args="filter=c.filter, route='referers'" />
<%include file="referers_list.mako" args="referers=c.referers, admin=c.admin"/>
<%include file="filter.paging.mako" args="filter=c.filter, route='referers'" />
