# -*- coding: utf-8 -*-
<%inherit file="/main.mako" />
%for article in c.articles:
<div>${article.index}. <a href="${h.url('help', handle=article.handle)}">${article.title}</a></div>
%endfor

<hr/>
<br class="clear" />
