# -*- coding: utf-8 -*-
<%inherit file="/main.mako" />
%if c.errors:
%for error in c.errors:
<div class="error">${error}</div>
%endfor
%endif
<%include file="/search_form.mako" />
<hr />
