# -*- coding: utf-8 -*-
<%inherit file="/main.mako" />
<div class="info">${_('Searched for "%s", found %s posts and %s files from %s threads.') % (c.search.query, c.search.count, c.search.files, len(c.search.threads))}</div>
<hr />
%for thread in c.threads:
     <%include file="/view/thread.mako" args="thread=thread, board=thread.board" />
%endfor
<%include file="/view/paginator.mako" args="route='search', kwarg={'search_id':c.search.id, 'ext':'xhtml'}" />
<%include file="/search_form.mako" />
<hr />
