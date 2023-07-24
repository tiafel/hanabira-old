<%page args="post, thread, board"/>
%if c.admin and c.can_view_ip:
<tr class="names">
<td>post</td>
<td>board</td>
<td>ip</td>
<td>password</td>
<td>session id</td>
</tr>
<tr class="values">
<td>${post.display_id} (<a href="${h.url('post_admin', post_id=post.post_id)}">${post.id}</a>)</td>
<td>/${board.board}/</td>
<td>${h.whois_link(post.ip) |n} ${h.geoip(post.geoip) |n}</td>
<td>${post.password}</td>
<td><a href="${h.url('session', session_id=post.session_id)}">${post.session_id}</a>
</td>
</tr>
%endif
<tr class="values">
<td colspan="6" style="text-align:left;">Thread 
<a style="font-weight:bold;" href="${h.url('thread_admin', thread_id=thread.id)}">${thread.display_id}</a> [${thread.id}] 
${thread.posts_count} posts.
<a style="font-weight:bold;" href="${h.url('thread', board=board.board, thread_id=thread.display_id)}" onmouseover="ShowRefPost(event,'${board.board}', ${thread.display_id}, ${thread.display_id})">    
    &gt;&gt;/${board.board}/${thread.display_id}
</a>
"${thread.title}"
</td>
</tr>
%if post.invisible or (post.op and thread.invisible):
<tr class="values"><td colspan="6" style="text-align:left;"><b>Invisible</b>, ${', '.join(post.inv_reason)}</td></tr>
%endif