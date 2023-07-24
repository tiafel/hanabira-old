# -*- coding: utf-8 -*-
<%inherit file="/header.mako" />
<link rel="stylesheet" type="text/css" href="${h.static_versioned('css/highlight.css')}" />
<script language="javascript" type="text/javascript" src="${h.static_versioned('js/editarea/edit_area_full.js')}"></script>
<script language="javascript" type="text/javascript">
    var edit = ${c.edit and 'true' or 'false'};
    var loaded = edit;
    function eaload()
    {
	editAreaLoader.init({
	    id : "code_edit_ta",
	    syntax: "${c.type}",
	    language: "ru",
	    allow_toggle: false,
	    min_height: 500,
	    replace_tab_by_spaces: 4,
	    start_highlight: true
	});
    }
    if (edit)
    {
	eaload();
    }
</script>
<div class="file-info"><a href="${h.static(c.file.path)}">${c.file.filename}</a>: ${c.file.show_metadata()}</div>
<div id="code_div">
<div id="code_toolbar">
<a onclick="code_view();">${_('View')}</a> <a onclick="code_edit();">${_('Edit')}</a> <a onclick="code_edit_simple();">${_('Edit (simple)')}</a>
</div>
<div id="code_view" ${c.edit and "style='display: none;'" or '' |n}>
${c.text_html |n}
</div>
<div id="code_edit" ${not c.edit and "style='display: none;'" or '' |n}>
<form action="${h.url('util_text_save', file_id=c.file.id, post_id=c.post.id)}" method="POST">
<textarea id="code_edit_ta" name="code" rows="40" cols="80">${c.text}</textarea><br/>
<input type="submit" value="${_('Save')}" />
</form>
</div>
</div>
