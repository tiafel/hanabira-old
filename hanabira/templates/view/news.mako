# -*- coding: utf-8 -*-
<%page args="news, board" />
 <div class="newsbg">
	<div class="newstop">
		<div class="newsbottom">
			<div class="newssize">
				<center>
${news.op.subject} ${news.op.date}
				</center>
				<br />
${news.op.message | n}
			<center><br /><a href="${h.url('thread', board=board.board, thread_id=news.display_id)}">
			${h.ugt("%s reply", "%s replies", news.posts_count - 1)}
			</a></center>
			</div>
		</div>
	</div>
</div>
