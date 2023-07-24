# -*- coding: utf-8 -*-
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">
    <head>
        <title>
	${c.channel.title}
	%if c.pageinfo and c.pageinfo.title:
	    &mdash; ${c.pageinfo.title}
	    %if c.pageinfo.subtitle:
	    &mdash; ${c.pageinfo.subtitle}
	    %endif
	    %if c.pageinfo.page and not c.reply:
      	    	(${c.pageinfo.page})
    	    %endif
	%endif
        </title>
   <meta http-equiv="Content-Type" content="text/html;charset=utf-8" />
    <meta name="generator" content="Hanabira 【花びら】 ${app_globals.settings.dist.version}" />
    <meta name="language" content="${c.pageinfo.language}" />
    %if c.pageinfo.keywords:
    <meta name="keywords" content="${c.pageinfo.keywords}" />
    %endif
    %if c.pageinfo.meta_description:
    <meta name="description" content="${c.pageinfo.meta_description}" />
    %endif
    <link rel="shortcut icon" type="image/x-icon" href="${h.static('favicon.ico')}" />
    <link rel="icon" type="image/x-icon" href="${h.static('favicon.ico')}" />
    <link href="${h.static_versioned('css/common.css')}" type="text/css" rel="stylesheet" />
    %for style_name, style_css in app_globals.styles:
    <link title="${style_name}" href="${h.static_versioned('css/%s'%style_css)}" type="text/css" rel="${style_name != app_globals.default_style and 'alternate ' or ''}stylesheet" />
    %endfor
    <script type="text/javascript" src="${h.static('js/jquery-1.3.2.js')}"></script>
    <script type="text/javascript" src="${h.static('js/jquery.form-3.51.js')}"></script>
    <script type="text/javascript" src="${h.static('js/jquery.progressbar-2.0.js')}"></script>
    <script type="text/javascript" src="${h.static('js/jquery.jplayer.mod-0.2.5.js')}"></script>
    <script type="text/javascript" src="${h.static_versioned('js/music.js')}"></script>
    <script type="text/javascript" src="${h.static_versioned('js/hanabira.js')}"></script>
    %if c.admin:
    <script type="text/javascript" src="${h.static_versioned('js/filters.js')}"></script>
    <script type="text/javascript" src="${h.static_versioned('js/gyousei.js')}"></script>
    %endif
    <script type="text/javascript">
    Hanabira.LC_ru = ${int('ru' in c.language)};
    Hanabira.ScrollAny = ${int(c.scroll_threads > 1)};
    </script>
    </head>
    <body onload="${c.onload or 'initialize()'}">
    ${next.body()}
    </body>
</html>
