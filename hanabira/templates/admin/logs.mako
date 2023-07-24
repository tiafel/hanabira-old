# -*- coding: utf-8 -*-
<%inherit file="admin.mako" />
<%include file="privacy.mako" />
<%include file="filter.mako" args="filter=c.filter" />
<%include file="filter.paging.mako" args="filter=c.filter, route='logs'" />
<%include file="logs_list.mako" args="events=c.logs, admin=c.admin"/>
<%include file="filter.paging.mako" args="filter=c.filter, route='logs'" />
