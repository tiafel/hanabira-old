# -*- coding: utf-8 -*-
<%inherit file="/main.mako" />

<center>
    <h2>${_('Error 404. Nothing to see here. Move along.')}</h2>
    <a href="javascript: history.go(-1)">${_('Back')}</a>
    <br /><br />
    <img height="500" src="${c._404image}"/>
</center>
    
<hr/>
<%include file="/search_form.mako" />