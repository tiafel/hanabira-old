# -*- coding: utf-8 -*-
<%inherit file="admin.mako" />
<%include file="filter.mako" args="filter=c.filter" />
<%include file="filter.paging.mako" args="filter=c.filter, route='files_list'" />
<table rules="all" style="border: 1px #000000 solid;">
%for f in c.files:
    <%include file="file.mako" args="f=f" />
%endfor
</table>
<%include file="filter.paging.mako" args="filter=c.filter, route='files_list'" />
