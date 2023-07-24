# -*- coding: utf-8 -*-
<%inherit file="/main.featured.mako" /><body>

<table width="100%" border="0" cellspacing="0" cellpadding="0">  <tr>
    <td class="logodobleft"></td>
    <td colspan="2" class="logodobright"><img src="/images/newlogo.png" alt="Logo"></td>
  </tr>
  <tr>
    <td valign="top" align="right">
<div style="float:right;"> 

%for img in c.featured_files:
<a href="${h.url('thread', board=img.board.board, thread_id=img.thread.display_id)}"><div style="width:200px; background-image:url(${img.thumb_path}); background-repeat:no-repeat; background-position:top center;">
	<div class="featuredimgtop">
		<div class="featuredimgbottom">			
		</div>
	</div>
</div></a>
%endfor
    
    </td>
    <td width="25" style="background-image:url(/css/img/green.png); background-repeat:repeat-y;"></td>
    <td valign="top">

%for post in c.featured_posts:
<%include file="news.mako" args="news=post.thread, board=post.board" />
%endfor
%if c.news:
%for news in c.news:
<%include file="news.mako" args="news=news, board=c.board" />
%endfor
%endif


    </td>
  </tr>
</table>
