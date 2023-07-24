# -*- coding: utf-8 -*-
<%page args="filter, route" />
<table class="pages"><tbody><tr><td>
%if filter.page > 0:
    <a href='${h.url(route, filter_id=filter.id, page=(filter.page - 1))}' class='paginator-arrow'>←</a>
%endif

<% in_skip_range = False %>
%for pg in range(0, filter.pages):
   %if pg == filter.page:
       [${pg}]
   %else:
       %if ((pg < 3) or ((pg + 3) >= filter.pages) or (filter.page - 3 < pg < filter.page + 3)):
       <% in_skip_range = False %>
       [<a href='${h.url(route, filter_id=filter.id, page=pg)}'>${pg}</a>]
       %elif not in_skip_range:
       ...
       <% in_skip_range = True %>
       %endif
   %endif
%endfor
%if filter.page < filter.pages-1:
    <a href='${h.url(route,  filter_id=filter.id, page=(filter.page + 1))}' class='paginator-arrow'>→</a>
%endif
</td></tr></tbody></table>
