var loaded_ips = {};
var is_admin = false;
function AutoRm(obj, time) {
  var to;
  rm = function() {to = setTimeout(function() {obj.remove()}, time)};
  obj.bind('mouseout', rm);
  obj.mouseover(function() {to && clearTimeout(to)});
  return rm;
}
whois = function(e, ip)
{
  var a	   = $(e.target);
  var to0 = setTimeout(function()
  {
    var w	= $(window).width();
    var x	  = e.pageX;
    var y	  = e.pageY + 30;
    var wx	= w - x;
    set_style = function(r) {
        r.attr('style', 'position: absolute; top: '+y+'px; max-width: '+wx+'px; '+'left: '+x+'px;');
    }
    var reftab;
    if (reftab = $('#'+ip)[0])
    {
      set_style(reftab);
      return;
    }
    reftab = $('<div id="'+ip+'" class="reply popup"></div>');
    set_style(reftab);
    $(document.body).append(reftab);
    BindRemoveRef(a, reftab[0]);
    
    var post = loaded_ips[ip];
    if (post)
      reftab.html(post);
    else
    {
      toLoading(reftab);
      $.get('/admin/whois/'+ip, {}, function(post, status) {
        set_style(reftab.html(loaded_ips[ip] = post.replace(/\n/gm, '<br>')).attr('class', 'reply popup'))}
      );
    }
  }, 200);
  
  a.mouseout(function() {clearTimeout(to0)});
}
function userpan_link(url, name, d)
{
   if (d)
      return '<a style="text-decoration:none" href="'+url+'" target="_blank">'+name+'</a><br/>';
   else 
      return '<a style="text-decoration:none" onclick="$.get(\''+url+'\'); return false;" href="'+url+'">' + name + '</a><br/>'
}
get_userpan = function(e, post, thread, session, hidden, deleted)
{
  if (!(
       (e.button == 1) || 
       (e.button == 0 && 
          (e.shiftKey || e.ctrlKey || e.altKey || e.metaKey)
          )
     ))
    return;
  var to;
  var a = $(e.target);
  var x	  = e.pageX - 20;
  var y	  = e.pageY - 160;
  var tab = $('<table style="top: '+y+'px; '+'left: '+x+'px; z-index: 255;" class="reply popup"><tr><td style="text-align:center">'+
   userpan_link('/admin/post/'+post+'.xhtml', 'get post', 1) +
   userpan_link('/admin/thread/'+thread+'.xhtml', 'get thread', 1) + 
   userpan_link('/admin/session/'+session, 'get session', 1) +
   userpan_link('/api/admin/post/'+post+'/reset-name', 'reset name') +
   userpan_link('/api/admin/post/'+post+'/delete-images', 'delete images') +   
   userpan_link('/admin/post/'+post+'/edit.xhtml', 'edit post', 1) +   
  (hidden ? 
   userpan_link('/api/admin/post/'+post+'/show.json', 'show') :
   userpan_link('/api/admin/post/'+post+'/hide.json', 'hide')) +
  (deleted ? userpan_link('/api/admin/post/'+post+'/revive.json', 'revive') : '') + 
  '</td></tr></table>');
  tab[0].style.zIndex = Hanabira.zIndex++;
  $(document.body).append(tab);
  AutoRm(tab, 100);
}
get_filepan = function(e, this_id, files_ids)
{
  if (!(
       (e.button == 1) || 
       (e.button == 0 && 
          (e.shiftKey || e.ctrlKey || e.altKey || e.metaKey)
          )
     ))
    return;
  var to;
  var a = $(e.target);
  var x	  = e.pageX - 20;
  var y	  = e.pageY - 40;
  var tab = $('<table style="top: '+y+'px; '+'left: '+x+'px;" class="reply popup"><tr><td style="text-align:center"><a>all files info</a><br></td></tr><tr><td style="text-align:center"><a>this file info</a><br></td></tr></table>');
  tab[0].style.zIndex = Hanabira.zIndex++;
  $(document.body).append(tab);
  tofunc = AutoRm(tab, 100);
  tab.find('a:first').click(function() {tab.load('/admin/file/ajax/'+files_ids, function() {
      tab.unbind('mouseout', tofunc);
      AutoRm(tab, 500);
  })});
  tab.find('a:last').click(function() {tab.load('/admin/file/ajax/'+this_id, function() {
      tab.unbind('mouseout', tofunc);
      AutoRm(tab, 500);
  })});
}
prepare_merge = function(e, subj, board)
{
  var x	  = e.pageX - 20;
  var y	  = e.pageY - 80;
  $(document.body).append($('<table id="merge_tab" style="top: '+y+'px; '+'left: '+x+'px;" class="reply popup"><tr><td style="text-align:center">I\'ll merge this thread<br>with another choosen by<br>display_id <input id="display_id" size="10"><br>on this board or<br>thread_id <input id="thread_id" size="10"><br>[<a onclick="cast_merge(\''+subj+'\', \''+board+'\')">Cast</a>]</td></tr></table>'));
}
cast_merge = function(subj, board)
{
  var tab = $('#merge_tab');
  var did = $('#display_id').val();
  if (did)
    $.getScript('/admin/thread/merge/'+subj+'/'+board+'_'+did)
  else
  {
    var tid = $('#display_id').val();
    if (tid)
      $.getScript('/admin/thread/merge/'+subj+'/'+tid);
    else
      tab.find('td').html('Spell cancelled');
  }
  setTimeout(function() {tab.remove()}, 1000);
}
prepare_transport = function(e, subj, board)
{
  var x	  = e.pageX - 20;
  var y	  = e.pageY - 80;
  $(document.body).append($('<table id="transport_tab" style="top: '+y+'px; '+'left: '+x+'px;" class="reply popup"><tr><td style="text-align:center">I\'ll export this thread<br>to another board<br>with name <input id="boardname" size="10"><br>[<a onclick="cast_transport(\''+subj+'\', \''+board+'\')">Cast</a>]</td></tr></table>'));
}
cast_transport = function(subj, board)
{
  var tab = $('#transport_tab');
  var bname = $('#boardname').val();
  if (bname)
    $.getScript('/admin/thread/transport/'+subj+'/'+board+'/'+bname)
  else
    tab.find('td').html('Spell cancelled');
  setTimeout(function() {tab.remove()}, 1000);
}
user_posts_stat = function(e)
{
  e.preventDefault();
  var form = e.target;
  if ($("[name='do']", form).val() == 'stat')
  {
    form.target = 'iframe';
    setTimeout(function() {$('#iframe').removeAttr('height')}, 500);
  }
  else
    form.removeAttribute('target');
  form.submit();
}
exec_delete = function(form)
{
  form.append($('<input type="hidden" name="do" value="delete" />'));
  form.submit();
}
cancel_delete = function(form)
{
  form.append($('<input type="hidden" name="do" value="cancel" />'));
  form.submit();
}
def_subnet = function(e, ip)
{
  var a = $(e.target);
  var input = $('#range', a.closest('form'));
  var range = input.val();
  if (range == '0.0.0.0 - 255.255.255.255')
    $.get('/admin/whois/'+ip, {}, function(post, status) {
      range = $(post).find('#subnet').val();
      input.val(range);
      $('#set_range').val(range);
    });
  var o = a.offset();
  var x	= o.left - 40;
  var y	= o.top - 100;
  $(document.body).append($('<table id="subnet_tab" style="position: absolute; top: '+y+'px; '+'left: '+x+'px;" class="reply popup"><tr><td style="text-align:center">Confirm received range<br><input onkeypress="if(event.which==13)set_range()" type="text" size="30" value="'+range+'" id="set_range"><br>or point yourself<br> [<a onclick="set_range()">Accept</a>] </td></tr></table>'));
}
set_range = function()
{
  $('#range').val($('#set_range').val());
  $('#subnet_tab').remove();
}
add_field = function(el, num)
{
  el && el.removeAttribute('onchange');
  $('#words_submit').before($('<input onchange="add_field(this, '+(num+1)+')" type="text" name="'+(num+1)+'" size="35"/> regexp: <input type="checkbox" name="re_'+(num+1)+'" checked="checked"/> for ops only: <input type="checkbox" name="op_'+(num+1)+'" checked="checked"/> auto penalty: <select name="ab_'+(num+1)+'"><option value="" selected="selected">none</option><option value="invis">invis</option><option value="ban">ban</option></select> message size: <input type="text" name="ts_'+(num+1)+'" size="5"/><br>'));
}

var delete_panel_visible = false;
var move_panel_visible = false;
function admin_delete_clicked(obj)
{
   var inp_checked = $('input:checked');
   if (inp_checked.length > 0 &&(!delete_panel_visible))
   {
      $('#admin_delete_panel').show();
      delete_panel_visible = true;
   }
   else if (inp_checked.length == 0 && delete_panel_visible)
   {
      $('#admin_delete_panel').hide();
      delete_panel_visible = false;   
   }
   if (inp_checked.length > 0)
   {
      var q_posts = inp_checked.length;
      var q_threads = 0;
      var q_ops = 0;
      var q_html = "";
      // Count posts and threads
      if (q_ops > 0)
          q_html = "<font style='color: #BB0000; font-weight: bold;'>"+q_ops+"</font>";
      else
          q_html = q_ops;
      $('#adp_posts_selected').html("Posts: "+q_posts+", Threads: "+q_threads+", OPs: "+q_html);
   }
}
function admin_delete_delete()
{
   $('#delete_form')[0].submit();
}
function admin_delete_move()
{
  if (!move_panel_visible)
  {
   var tab = $('<table id="move_panel" style="position: fixed; bottom: 300px; top: auto; left: 200px; z-index: 255;" class="reply popup"><tr><td style="text-align:left">'
   +
   'Move selected posts: <br/>'
   +
   '<input type="radio" name="move_target" value="board"> new thread (other board): <input type="text" name="move_board"><br/>'
   +
   '<input type="radio" name="move_target" value="new_thread"> new thread (same board).<br/>'
   +
   '<input type="radio" name="move_target" value="thread_display_id"> existing thread (display_id): <input type="text" name="move_thread_display_id"><br/>'
   +
   '<input type="radio" name="move_target" value="thread_id"> existing thread (thread_id): <input type="text" name="move_thread_id"><br/>'
   +
   '<input type="checkbox" name="old_thread" checked="checked"/> Keep existing thread</br>'
   +
   '<input type="button" value="Move" onclick="move_panel_submit();"/> <input type="button" value="Close" onclick="move_panel_hide();"/>'
   +
   '</td></tr></table>');
   tab[0].style.zIndex = Hanabira.zIndex++;
   $(document.body).append(tab);
   move_panel_visible = true;
  }
   //AutoRm(tab, 100);

}
function move_panel_hide()
{
   if (move_panel_visible)
   {
      $("#move_panel").remove();
      move_panel_visible = false;
   }
}
function move_panel_submit()
{
   var df = $('#delete_form');
   df[0].action = '/admin/post/move';
   df.append($("#move_panel input").detach());
   df[0].submit();
}
function admin_delete_unselect()
{
   var ch = $("input:checked");
   ch.prop("checked", false);
   ch.parent().toggleClass('checked');
   $('#admin_delete_panel').hide();
   delete_panel_visible = false;     
}
function admin_toggle_post_panel(t, pid)
{
  $('#admin_panel_'+t+'_'+pid+'_1').toggle();
  $('#admin_panel_'+t+'_'+pid+'_2').toggle();  
}

function admin_posts_del_all()
{
  $(".delete input").each(function() {
     if (!this.checked) this.click();
  });
}
function admin_posts_del_unselect()
{
  $(".delete input").each(function() {
     if (this.checked) this.click();
  });
}
function admin_posts_del_inv()
{
  admin_posts_del_unselect();
  $("label img[alt='Invisible']").parent().
    children(".delete").children("input").
    each(function ()
      {
      if (!this.checked) this.click();
      }
    );
}
function admin_posts_remove_post(post_id)
{
  $("#post_"+post_id).hide('fast');
}
function admin_posts_post_del(e, post_id, d)
{
  e.target.disabled = true;
  $.post('/api/admin/post/'+post_id+'/delete.json', {'reason':''}, 
  function (res, status)
  {
    if (d)
      admin_posts_remove_post(post_id);
    else
      $(e.target).remove();      
  }
  );
}
function admin_posts_post_revive(e, post_id, d)
{
  e.target.disabled = true;
  $.get('/api/admin/post/'+post_id+'/revive.json', {}, function (res, status)
  {
    if (d)
      admin_posts_remove_post(post_id);
    else
      $(e.target).remove();      
  }
  );
}
function admin_posts_post_show(e, post_id, d, b)
{
  e.target.disabled = true;
  var url = '/api/admin/post/'+post_id+'/show.json';
  if (b == 1)
    url += '?bump=1';
  $.get(url, {}, function (res, status)
  {
    if (d)
      admin_posts_remove_post(post_id);
    else
      $(e.target).remove();
  }
  );
}
function admin_thread_toggle_attr(thread_id, attrname, e)
{
  var li = $(e.target).parent();
  var oldval = li.children("input[type='hidden']").val();
  if (oldval == 0 || !oldval)
      var newval = 1;
  else 
      var newval = 0;
  e.target.disabled = true;
  $.get('/api/admin/thread/'+thread_id+'/set/'+attrname+'/'+newval+'.json', {}, function (res, status)
  {
    e.target.disabled = false;
    var r = res['result'];
    li.children("input[type='hidden']").val(r);
    if (r == 1)
       var valstr = "on";
    else
       var valstr = "off";
    li.children('span').html(valstr);
  }
  )
}