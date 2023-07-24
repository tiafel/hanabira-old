# -*- coding: utf-8 -*-
<%inherit file="admin.mako" />
<script>files_max_qty=5</script>
<%include file="privacy.mako" />

%if c.last_posts_req:
<form action="/admin/exec/lastposts" method="post">
%for k,v in c.last_posts_req.items():
<input type="hidden" name="${k}" value="${v}"/>
%endfor
<input type="submit" value="Reload list"/>
</form>
%endif

%if not c.view.has_lookup:
<form action="/admin/exec/userposts" method="post">
<input type="hidden" name="do" value="delform">
<input type="submit" value="Delete">
<input type="button" value="Select inv"   onclick="admin_posts_del_inv()"/>
<input type="button" value="Select all"   onclick="admin_posts_del_all()"/>
<input type="button" value="Unselect all" onclick="admin_posts_del_unselect()"/>
%endif

%for post in c.posts:
<%include file="post.mako" args="view=c.view, post=post, thread=post.thread, board=post.thread.board"/>
%endfor

%if not c.view.has_lookup:
</form>
%if c.check_boxes:
<script type="text/javascript">
admin_posts_del_inv();
</script>
%endif
%endif

%if c.events:
<%include file="logs_list.mako" args="events=c.events, admin=c.admin"/>
%endif
