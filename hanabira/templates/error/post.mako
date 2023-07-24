# -*- coding: utf-8 -*-
<%inherit file="/main.mako" />
%if c.error_message:
<center><h2>${c.error_message |n}</h2></center>
%else:
<%include file="/newpost.mako" />
%endif
<hr/>
<br class="clear" />

