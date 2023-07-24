<%include file="post_data.mako" args="post=c.post, thread=c.thread, board=c.board"/>
<tr class="logo" style="font-size:1.5em;"><td colspan="6">Spells for</td></tr>
<tr><td class="postblock logo" style="font-size:1em;" colspan="6">user</td></tr>
<tr><td colspan="6"><form action="/admin/exec/user" method="post"> cast
<input type="hidden" name="post_id" value="${c.post.id}" />
<select name="act">
    <option value="inv">invisibility</option>
    <option value="ban">ban</option>
</select> on this 
<input type="hidden" id="range" name="range" value="0.0.0.0 - 255.255.255.255" />
<select onchange="if(this.value=='sn')def_subnet(event, '${c.post.ip}')" name="target">
    <option value="ip">ip</option>
    <option value="sn">subnet</option>
</select> for 
<input id="usertime" style="display:none" name="qty" type="text" value="120" size="5"/>
<select onchange="this.value=='ev'?$('#usertime').hide():$('#usertime').show()" name="limit">
    <option value="ev">ever</option>
    <option value="hr">hours</option>
    <option value="ds">days</option>
</select>
<input type="submit" value="Cast">
</form></td></tr>
<tr><td class="postblock logo" style="font-size:1em;" colspan="6">
user posts</tr>
<tr><td colspan="6"><form onsubmit="user_posts_stat(event)" action="/admin/exec/userposts" method="post">
<input type="hidden" name="post_id" value="${c.post.id}" />
<input type="hidden" name="board" value="${c.board.board}" />
<select onchange="this.value=='del'?$('#max').hide():$('#max').show()" name="do">
    <option value="list">list</option>
    <option value="stat">count</option>
</select> posts by 
<input type="hidden" id="range" name="range" value="0.0.0.0 - 255.255.255.255" />
<select onchange="if(this.value=='sn')def_subnet(event, '${c.post.ip}')" name="by">
    <option value="ss">session</option>
    <option value="pw">password</option>
    <option value="pi">password or ip</option>
    <option value="ip">ip</option>
    <option value="ad">any data</option>
    <option value="sn">subnet</option>
</select> of this post for
<span id="postslimit" style="display:none">last <input name="qty" type="text" size="5"/></span>
<select onchange="this.value=='ev'?$('#postslimit').hide():$('#postslimit').show()" name="limit">
    <option value="ev">ever</option>
    <option value="hr">hours</option>
    <option value="ds">days</option>
    <option value="ps">posts</option>
</select>
<select name="ops">
    <option value="in">including</option>
    <option value="ex">excluding</option>
    <option value="is">that is</option>
</select> op posts from
<select name="loc">
    <option value="oa">overall</option>
    <option value="tt">this thread</option>
    <option value="tb">this board</option>
    <option value="ba">board+archive</option>
</select>
<span id="max">limit <input type="text" size="5" name="max" value="50"/></span>
<input id="upsm" type="submit" value="Show" />
</form></td></tr>
<tr><td colspan="6"><iframe id="iframe" name="iframe" width="100%" height="0" frameborder="0" border="0" src="about:blank"></iframe></td></tr>
