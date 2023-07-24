# -*- coding: utf-8 -*-
<html>
    <head>
        <title>
	${app_globals.settings.chan.title}
	%if c.pageinfo and c.pageinfo.title:
	    &mdash; ${c.pageinfo.title}
	    %if c.pageinfo.subtitle:
	    &mdash; ${c.pageinfo.subtitle}
	    %endif
	    %if c.pageinfo.page:
      	    	(${c.pageinfo.page})
    	    %endif
	%endif
        </title>
        <meta http-equiv="Content-Type" content="text/html;charset=utf-8" />
	<meta name="generator" content="Hanabira 【花びら】 ${app_globals.settings.dist.version}" />
	<meta name="language" content="${c.pageinfo.language}" />
        <link rel="shortcut icon" type="image/x-icon" href="${h.static('favicon.ico')}" />
        <link rel="icon" type="image/x-icon" href="${h.static('favicon.ico')}" />
        <link href="${h.static_versioned('css/common.css')}" type="text/css" rel="stylesheet" />
	%for style_name, style_css in app_globals.styles:
        <link title="${style_name}" href="${h.static_versioned('css/' + style_css)}" type="text/css" rel=${style_name == app_globals.default_style and '"' or '"alternate ' | n}stylesheet" />
	%endfor
	<style type="text/css"> body { background: #9999BB; font-family: sans-serif; } input,textarea { background-color:#CFCFFF; font-size: small; } table.nospace { border-collapse:collapse; } table.nospace tr td { margin:0px; }  .menu { background-color:#CFCFFF; border: 1px solid #666666; padding: 2px; margin-bottom: 2px; } </style>
    </head>
<body>
<script type="text/javascript" src="/files/shi/sp.js"></script>
<script type="text/javascript" src="/files/shi/selfy.js"></script>
<table cellpadding="0" cellspacing="0"  class="nospace" height="100%" width="100%" style="height: 100%;">
  <tr>
    <td width="100%">
      <applet width="100%" height="100%" code="c.ShiPainter.class" codebase="/" name="paintbbs" archive="/files/shi/spainter.jar,/files/shi/res/${c.shi_type}.zip" MAYSCRIPT>
	<param name="image_width" value="${c.width}" />
	<param name="image_height" value="${c.height}" />
	<param name="image_canvas" value="" />
	<param name="compress_level" value="15" />
	<param name="url_save" value="${h.url('util_shi_save', file_id=c.file_id, file_key=c.file_key)}" />
	<param name="url_exit" value="${h.url('post_error', post_id=c.post_id)}" />
	<param name="send_header_image_type" value="true" />
	<param name="send_header_timer" value="true" />
	<param name="dir_resource" value="/files/shi/res/" />
	<param name="tt.zip" value="/files/shi/res/tt.zip" />
	<param name="res.zip" value="/files/shi/res/res_${c.shi_type}.zip" />
	<param name="tools" value="${c.shi_type}" />
	<param name="layer_count" value="3" />
	<param name="quality" value="1" />
	<param name="undo_in_mg" value="15" />
	<param name="undo" value="30" />
	<param name="MAYSCRIPT" value="true" />
	<param name="scriptable" value="true" />
	<param name="image_canvas" value="${c.source}" />
%if c.animation:
    <param name="thumbnail_type" value="animation" />
    %if c.pchPath:
        <param name="pch_file" value="${c.pchPath}" />
    %endif
%endif
      </applet>
    </td>
  </tr>
</table>
</body>
</html>
