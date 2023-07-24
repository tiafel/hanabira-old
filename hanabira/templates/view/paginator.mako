# -*- coding: utf-8 -*-
<%page args="route, kwarg={}"/>

%if c.pages:
<table class="pages"><tbody><tr><td>
%if c.pageinfo.page > 0:
    <a href='${h.url(route, **(dict(kwarg, **dict(page=(c.pageinfo.page - 1) or 'index'))))}' class='paginator-arrow'>←</a>
%endif

<% in_skip_range = False %>
%for pg in range(0,c.pages):
   %if pg == c.pageinfo.page:
       [${pg}]
   %else:
       %if ((pg < 6) or ((pg + 3) >= c.pages) or (c.pageinfo.page - 3 < pg < c.pageinfo.page + 3)):
       <% in_skip_range = False %>
       [<a href='${h.url(route, **(dict(kwarg, **dict(page=pg or 'index'))))}'>${pg}</a>]
       %elif not in_skip_range:
       ...
       <% in_skip_range = True %>
       %endif
   %endif
%endfor
%if c.pageinfo.page < c.pages-1:
    <a href='${h.url(route, **(dict(kwarg, **dict(page=str(c.pageinfo.page + 1)))))}' class='paginator-arrow'>→</a>
%endif
</td></tr></tbody></table>
%endif
