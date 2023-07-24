# -*- coding: utf-8 -*-
<%page args="thread, board"/>
%for post in thread.posts:
    %if post.op:
  <div id="post_${post.display_id}" class="oppost post">
    %else:
  <table id="post_${post.display_id}" class="replypost post"><tbody><tr>
    %if not c.mini:
  <td class="doubledash">&gt;&gt;</td>
    %endif
  <td class="reply" id="reply${post.display_id}">
    %endif
    <%include file="post.mako" args="board=board, thread=thread, post=post" />
    %if post.op:
  </div>
    %else:
  </td></tr></tbody></table>
    %endif
%endfor