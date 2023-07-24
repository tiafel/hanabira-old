# -*- coding: utf-8 -*-
<%inherit file="admin.mako" />
<%include file="privacy.mako" />
<%def name="session_posts(op=False, invisible=False, deleted=False)">
<form action="${h.url('userposts')}" method="POST">
<input type="hidden" name="do" value="list"/>
<input type="hidden" name="by" value="ss"/>
<input type="hidden" name="limit" value="ev"/>
<input type="hidden" name="board" value="b"/>
<input type="hidden" name="loc" value="oa"/>
<input type="hidden" name="ops" value="in"/>
<input type="hidden" name="max" value="50"/>
<input type="hidden" name="session_id" value="${c.session_id}"/>
<input type="hidden" name="deleted" value="${deleted and 1 or 0}"/>
<input type="hidden" name="is_op" value="${op and 1 or 0}"/>
<input type="hidden" name="invisible" value="${invisible and 1 or 0}"/>
<li> ${caller.body()}
<input type="submit" value="Find" />
</li>
</form>
</%def>
<ul>
%if c.session.admin:
<hr>
<li>${_('Account')}: ${c.session.admin.login}</li>
%endif
<hr>
<li>${_('Created at')}: ${h.show_time(c.session.created_at, c, True)}</li>
<li>${_('Last active')}: ${h.show_time(c.session.last_active, c)}</li>
%if c.session.last_posted:
<li>${_('Last post')}: ${h.show_time(c.session.last_posted, c)}</li>
%endif
<li>${_('First IP')}: ${c.session.created_ip}</li>
<li>${_('Last IP')}: ${c.session.last_ip}</li>
<li>${_('Password')}: ${c.session.password}</li>
%if c.session.referer:
<li>${_('Referer')}: ${c.session.referer}</li>
%endif
<%call expr="session_posts()">
${_('Post count')}: ${c.session.posts_count} 
</%call>
<form method="POST">
<li>Добавить глобальную премодерацию, причина: 
<input id="reason" name="premod_reason" type="text" />
<input type="submit" value="Добавить"/>
</li>
</form>
%if c.session.tokens:
<li>Ограничения:</li>
</ul>
<table style="border: 1px #000000 solid;">
<tr>
  <td>Тип</td>
  <td>Область</td>
  <td>Дата</td>
  <td>Причина</td>
  <td>Админ</td>
  <td></td>  
</tr>
%for token, scope, duration, date_start, opts in c.session.tokens:
<tr>
  <td>${token}</td>
  <td>
  %if scope[0] == 'thread':
  <a href="${h.url('thread_admin', thread_id=scope[1])}">${"{0[0]}:{0[1]}".format(scope)}</a>
  %else:
  ${scope[0] == 'global' and 'global' or "{0[0]}:{0[1]}".format(scope)}
  %endif
  </td>
  <td>${date_start} — ${duration == -1 and u"Бессрочно" or date_start + duration}</td>
  <td>
  %if 'reason_post_id' in opts:
  <a href="${h.url('post_admin', post_id=opts['reason_post_id'])}">Пост ${opts['reason_post_id']}</a>
  %endif
  %if 'reason_text' in opts:
  ${opts['reason_text']}
  %endif
  %if 'reasons' in opts:
  ${h.format_reasons_short(opts['reasons'])}
  %endif
  <td>${'admin' in opts and opts['admin'] or 'auto'}</td>
  <td><form method="POST"><input type="hidden" name="token_data" value="${"{0}:{1}:{2}".format(token, scope[0], scope[1])}"><input type="submit" value="Отключить"/></form></td>
</tr>
%endfor
</table>
<ul>
%else:
<li>Ограничений нет.</li>
%endif
%if c.session.posts_count:
<li>${_('Chars per post')}: ${c.session.posts_chars / c.session.posts_count}</li>
%endif
<li>${_('Visible posts')}: ${c.session.posts_visible}</li>

<%call expr="session_posts(deleted=True)">
${_('Deleted posts')}: ${c.session.posts_deleted}
</%call>

<%call expr="session_posts(invisible=True)">
${_('Invisible posts')}: ${c.session.posts_invisible}
</%call>

<%call expr="session_posts(op=True)">
${_('Threads count')}: ${c.session.threads_count}
</%call>

<%call expr="session_posts(op=True, deleted=True)">
${_('Deleted threads')}: ${c.session.threads_deleted}
</%call>

<%call expr="session_posts(op=True, invisible=True)">
${_('Invisible threads')}: ${c.session.threads_invisible}
</%call>
</ul>
<form method="POST" action="${h.url("session_recount", session_id=c.session_id)}">
<input type="submit" value="Recount posts"/>
</form>
%if c.warnings:
<br/>История ограничений/предупреждений для сессии и подсетей:<br/>
<table style="border: 1px #000000 solid;">
<tr>
  <td>Тип</td>
  <td>Дата</td>
  <td>Сессия</td>
  <td>IP</td>  
  <td>Причина</td>
</tr>
%for wr in c.warnings:
<tr>
  <td>${wr.token == 'none' and u'Предупреждение' or wr.token}</td>
  <td>${wr.date}</td>
  <td>
  %if wr.session_id == c.session.id:
  (эта сессия)
  %else:
  <a href="${h.url('session', session_id=wr.session_id)}">${wr.session_id}</a>
  %endif
  </td>
  <td>${h.whois_link(wr.ip) |n}</td>
  <td>
  %if wr.post_id:
  <a href="${h.url('post_admin', post_id=wr.post_id)}">Пост ${wr.post_id}</a>
  %endif
  ${wr.reason}
  </td>
</tr>
%endfor
</table>
%endif
%if c.events:
<br/>Журнал действий с сессией:<br/>
<%include file="logs_list.mako" args="events=c.events, admin=c.admin"/>
%endif
%if c.referers:
<%include file="referers_list.mako" args="referers=c.referers, admin=c.admin"/>
%endif
