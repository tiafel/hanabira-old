<%inherit file="../header.mako" />
                <center>I have found<br>
                ${c.report}.<br>
                Do you wish me to remove them or forget about it?
                <form action="/admin/exec/userposts" method="post" id="frame_form">
                <input type="hidden" name="query" value="${c.query_id}">
                [<a onclick="exec_delete($(this.parentNode))">Remove</a>] [<a onclick="cancel_delete($(this.parentNode))">Forget</a>]
                </form></center>