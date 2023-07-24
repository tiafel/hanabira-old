<div class="logo">
     %if app_globals.settings.chan.debug:
        [DEBUG]
     %endif
     %if c.banner:
     	 <a href="${h.url('board', board=c.banner[0])}"><img class="banner" src="${c.banner[1]}" alt="/${c.banner[0]}/" title="/${c.banner[0]}/" /></a><br/>
     %endif
     ${c.pageinfo.chan_title}
     %if c.pageinfo and c.pageinfo.title:
	&mdash; ${c.pageinfo.title_logo}
	%if c.pageinfo.page and not c.reply:
	    (${c.pageinfo.page})
	%endif
	%if c.pageinfo.description:
	<br /><span class="description">${c.pageinfo.description}</span>
	%endif
	%if c.pageinfo.subtitle:
	<br /><span class="subtitle">${c.pageinfo.subtitle}</span>
	%endif
     %endif
</div>
