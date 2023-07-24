<%page args="view, post, thread, board"/>

<%def name="thread_options_attr_li(attrname)">
<li>
<input type="hidden" value="${int(getattr(thread, attrname))}"/>
${attrname}: <span>${getattr(thread, attrname) and "on" or "off"}</span>
<input type="button" value="Toggle" onclick="admin_thread_toggle_attr(${thread.thread_id}, '${attrname}', event);"/>
</li>
</%def>


<table id="post_${post.id}" style="${view.style_top_tab|n}">

%if view.admin and view.can_view_ip:
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
    %if c.session:
    %if c.session.get_token(['premod', 'forbid_post']):
    Глобальный бан/премод
    %else:
    Нет бана
    %endif
    %endif
</td>
</tr>
%endif

## Thread info
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


## Options bar
<tr class="values">
<td colspan="6" style="text-align:left;">
<a style="font-weight:bold;" onclick="admin_toggle_post_panel('thread', ${post.post_id})">[[ Thread options ]]</a> 
<a style="font-weight:bold;" onclick="admin_toggle_post_panel('user', ${post.post_id})">[[ Warning/Ban options ]]</a> 
%if view.has_lookup:
<a style="font-weight:bold;" onclick="admin_toggle_post_panel('lookup', ${post.post_id})">[[ Lookup user posts ]]</a> 
%endif
</td>
</tr>

## Panel - warning/ban options
<tr id="admin_panel_user_${post.id}_1" style="${view.style_panel_user}">
<td class="postblock logo" style="font-size:1em;" colspan="6">User</td>
</tr>
<tr id="admin_panel_user_${post.id}_2" style="${view.style_panel_user}">
<td colspan="6">
%if view.extended:
<form id="admin_panel_user_form_${post.id}" method="POST" action="${h.url('warnban_user', post_id=post.id)}" onsubmit="$(this).ajaxSubmit(function(){$('#admin_panel_user_buttons_${post.id}').remove();}); $('#admin_panel_user_buttons_${post.id}').children().prop('disabled', true); return false;">
%else:
<form id="admin_panel_user_form_${post.id}" method="POST" action="${h.url('warnban_user', post_id=post.id)}" onsubmit="$(this).ajaxSubmit(function(){admin_posts_remove_post(${post.id});}); return false;">
%endif
<b>Причина:</b></br>
%for warn_r_id, warn_r_name in view.warn_reasons_list:
<label><input type="checkbox" name="admin_user_warn_reason[]" value="${warn_r_id}"/>${warn_r_name}</label></br>
%endfor
<br/>
<label><input type="checkbox" name="admin_user_warn_send" checked/> Отправить пользователю уведомление/предупреждение</label></br>
<b>Ограничения:</b><br/>
<select name="admin_user_token_type">
<option value="none">Не добавлять ограничений</option>
<option value="forbid_post">Запрет писать посты</option>
<option value="premod">Премодерация</option>
<option value="bypass_premod">Разрешение публикации без премодерации</option>
<option value="forbid_name">Запрет использовать поле имя</option>
<option value="forbid_name_subj">Запрет использовать поле имя и поле тема</option>
<option value="forbid_files">Запрет загружать файлы</option>
</select>
<select name="admin_user_token_scope">
<option value="thread">Для треда >>${thread.display_id}</option>
<option value="board">Для раздела /${board.board}/</option>
<option value="global">Во всех разделах</option>
</select>
<select name="admin_user_token_duration">
<option value="10">10 минут</option>
<option value="30">30 минут</option>
<option value="60">1 час</option>
<option value="1440">24 часа</option>
<option value="2880">48 часов</option>
<option value="10080">1 неделя</option>
<option value="43200">1 месяц</option>
<option value="-1">Бессрочно</option>
</select><br/>
<label><input type="checkbox" name="admin_user_token_add_subnet"/> Добавить такое же правило для подсети</label><br/>
<input id="admin_panel_user_aa_${post.id}" type="hidden" name="additional_action" value=""/>
<span id="admin_panel_user_buttons_${post.id}">
<input type="submit" value="Delete + Warn/Ban" onclick="$('#admin_panel_user_aa_${post.id}').val('del');"/>
<input type="submit" value="Warn/Ban" onclick="$('#admin_panel_user_aa_${post.id}').val(''); "/>
%if post.invisible or (post.op and thread.invisible):
<input type="submit" value="Visible + Warn/Ban" onclick="$('#admin_panel_user_aa_${post.id}').val('vis');"/>
%endif
</span>
</form>
</td>
</tr>

## Panel - thread options
<tr id="admin_panel_thread_${post.id}_1" style="${view.style_panel_thread}"><td class="postblock logo" style="font-size:1em;" colspan="6">thread</td></tr>
<tr id="admin_panel_thread_${post.id}_2" style="${view.style_panel_thread}"><td colspan="6" class="value">
Attributes:
<ul>
${thread_options_attr_li('autosage')}
${thread_options_attr_li('archived')}
${thread_options_attr_li('sticky')}
${thread_options_attr_li('locked')}
${thread_options_attr_li('op_moderation')}
${thread_options_attr_li('censor_lim')}
${thread_options_attr_li('censor_full')}
</ul>
<input type="button" value="Merge" onclick="prepare_merge(event, ${thread.id}, '${board.board}')"/>
<input type="button" value="Set premod" onclick="$.post('${h.url('restrictions_new')}', {type:'thread',effect:'premod',value:${thread.id}})"/>
<input type="button" value="Clean invisible posts" onclick="$.get('/admin/thread/clean/${thread.id}')"/>
<input type="button" value="Delete thread" onclick="admin_posts_post_del(event, ${thread.op_id}, 0);"/>
</td></tr>

## Panel - posts Lookup
%if view.has_lookup:
<tr id="admin_panel_lookup_${post.id}_1" style="${view.style_panel_lookup}"><td class="postblock logo" style="font-size:1em;" colspan="6">
user posts</tr>
<tr id="admin_panel_lookup_${post.id}_2" style="${view.style_panel_lookup}"><td colspan="6">
<form action="/admin/exec/userposts" method="post">
<input type="hidden" name="post_id" value="${post.id}" />
<input type="hidden" name="board" value="${board.board}" />
<input type="hidden" name="do" value="list"/>
<input type="hidden" name="qty" value="0"/>
<input type="hidden" name="limit" value="ev"/>
<input type="hidden" id="range" name="range" value="0.0.0.0 - 255.255.255.255" />
Lookup posts by 
<select name="by">
    <option value="ss">session</option>
    <option value="ip">ip</option>
    <option value="sn">subnet</option>
</select> of this post
<select name="ops">
    <option value="in">including</option>
    <option value="ex">excluding</option>
    <option value="is">that is</option>
</select> posts from
<select name="loc">
    <option value="oa">overall</option>
    <option value="tt">this thread</option>
    <option value="tb">this board</option>
    <option value="ba">board+archive</option>
</select>
limit <input type="text" size="5" name="max" value="50"/>
<input type="submit" value="Show" />
</form>
</td></tr>
%endif 

<tr>
<td colspan="6" class="reply"${post.op and 'style="background-color:inherit"' or '' |n}>
<%include file="../view/post.mako" args="board=post.thread.board, thread=post.thread, post=post" />
</td>
</tr>

<tr class="values">
<td colspan="6" style="text-align:left;">
%if not post.deleted:
<input type="button" value="Delete" onclick="admin_posts_post_del(event, ${post.post_id}, ${int(not view.extended)});"/> 
%else:
<input type="button" value="Revive" onclick="admin_posts_post_revive(event, ${post.post_id}, ${int(not view.extended)});"/>
%endif
%if post.invisible or (post.op and thread.invisible):
<input type="button" value="Make visible" onclick="admin_posts_post_show(event, ${post.post_id}, ${int(not view.extended)}, 0);"/>
<input type="button" value="Visible + Bump" onclick="admin_posts_post_show(event, ${post.post_id}, ${int(not view.extended)}, 1);"/>
%endif
</td>
</tr>
</table>