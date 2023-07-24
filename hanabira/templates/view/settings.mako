# -*- coding: utf-8 -*-
<%inherit file="/main.mako" />
<table><tr><td style="padding-right: 20px; vertical-align:top">
    <form method="POST" id="ajax-form">
<table>
    <tr>
      <td colspan="2" class="logo">${_('Censorship ratings')} [<a href="${h.url('help', handle='censorship-ratings')}">?</a>]</td>
    </tr>
    <%include file="setting.mako" args="title='Max allowed rating', opts={'sfw':'SFW', 'r-15':'R-15', 'r-18':'R18', 'r-18g':'R-18G'}, name='rating', ajax=1" />
		<%include file="setting.mako" args="title='Show unrated', name='rating_strict', ajax=1, type='checkbox'" />
    <tr>
      <td colspan="2" class="logo">${_('Reputation')}</td>
    </tr>
    <%include file="setting.mako" args="title='Minimal reputation', name='reputation_min', ajax=1, type='text'" />
    <tr>
      <td colspan="2" class="logo">${_('Interface')}</td>
    </tr>
    <%include file="setting.mako" args="title='Language', opts={'ru':u'Русский', 'en':u'English', 'ru_ua':u'Дореволюцiонная орѳографiя', 'ja':u'日本語'}, name='language', ajax=1" />
    <%include file="setting.mako" args="title='Banners', opts={'different':'Different boards', 'same':'Same board', 'none':'No banners'}, name='banners', ajax=1" />
    <%include file="setting.mako" args="title='Reply button', opts={0:'within post num', 1:'separate'}, name='reply_button', ajax=1, hint='Merges reply button with post number link'" />
    %if c.mini_browser:
		<%include file="setting.mako" args="title='Mobile mode', name='mini', ajax=1, type='checkbox'" />
		<%include file="setting.mako" args="title='Disable postform', name='nopostform', ajax=1, type='checkbox'" />
    %endif
    <tr>
      <td colspan="2" class="logo" title="${_('Scroll thread to the last post you are replied while redirecting to thread')}">${_('Autoscroll')}</td>
    </tr>
    <%include file="setting.mako" args="title='Scroll', opts={2:'every time', 1:'if replied from thread', 0:'never'}, name='scroll_threads', ajax=1, hint='Scroll thread to the last post you are replied while redirecting to thread'" />
</table>
    </form>
    <form id="js-form">
<table>
    <tr>
      <td colspan="2" class="logo" title="${_('Popup behaviour')}">${_('Reflinks')}</td>
    </tr>
    <%include file="setting.mako" args="title='Appearance', opts={2:'above', 0:'below'}, name='rfpos'" />
    <%include file="setting.mako" args="title='Removing', opts={1:'on mouse out', 0:'by button & Esc'}, name='rmrf'" />
    <tr>
      <td colspan="2" class="logo" title="${_('This will always set \"Go back to\" to selected redir, \"auto\" sets redir to current page when posting from board and to thread otherwise. Without default goback just remember last choice')}">${_('Go back to')}</td>
    </tr>
    <%include file="setting.mako" args="title='Default', opts={0:'none', 4:'thread', 8:'board', 16:'current page', 32:'auto'}, name='redir'" />
    <tr>
      <td colspan="2" style="text-align:center">
        <input type="button" value="${_('Accept')}" onclick="set_opts('${c.referer or ''}')">
      </td>
    </tr>
    <tr>
      <td colspan="2" style="text-align:center" id="done"> </td>
    </tr>
</table>
</form>

%if c.hidden:
</td><td class="threadlist">
    <span class="logo">${_('Hidden threads')}:</span><br />
    %for b in c.hidden:
        <span style="font-weight:bold; font-size: 1.2em">/${b}/:</span><br />
        %for n in c.hidden[b]:
        %for t in c.hidden[b][n]:
            <span${n and ' style="display:none"' or '' |n}><a href="${h.url('thread', board=b, thread_id=t)}">№${t}</a>
            [<a onclick="unhide_thread(event, '${b}',${t})">${_('Unhide')}</a>]
            <br /></span>
        %endfor
        %if c.hidden[b][1] and not n:
            <span><a onclick="ExpandList(this)">${_("List other %s")%len(c.hidden[b][1])}</a><br /></span>
        %endif
        %endfor
    %endfor
%endif
</td></tr></table>
<script>fill_opts();</script>
<hr/>
<br class="clear" />
