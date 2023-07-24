# -*- coding: utf-8 -*-
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Frameset//EN" "http://www.w3.org/TR/html4/frameset.dtd">
<html>
    <head>
        <title>${app_globals.settings.chan.title}</title>
        <meta http-equiv="Content-Type" content="text/html;charset=utf-8" />
        <link rel="shortcut icon" type="image/x-icon" href="${h.static('favicon.ico')}" />
        <link rel="icon" type="image/x-icon" href="${h.static('favicon.ico')}" />
    </head>
    <frameset cols="210,*">
        <frame src="${h.url('frame')}" name="list" noresize scrolling="auto" frameborder="1" />
        <frame src="${h.url('main')}" name="board" noresize />
    </frameset>
</html>
