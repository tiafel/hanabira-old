player_active = 0;
play_item = 0;
playlist_index = {};
jplayer = null;
function show_music_player()
{
    if (!player_active)
    {
	$('#music_player').show("slow");
	player_active = 1;
    }
}
function hide_music_player()
{
    if (player_active)
    {
	$('#music_player').hide("slow");
	player_active = 0;
    }
}
function toggle_music_player()
{
    if (!player_active)
    {
	show_music_player();
    }
    else
    {
	hide_music_player();
    }
}
function init_music_player()
{
    jplayer = $("#jquery_jplayer").jPlayer({
	ready: function () {
	    reindex_playlist();
	    playlist_init(false);
	    return true;
	},
	swfPath: '/swf'
    });
    jplayer.jPlayerId("play", "player_play")
    .jPlayerId("pause", "player_pause")
    .jPlayerId("stop", "player_stop")
    .jPlayerId("loadBar", "player_progress_load_bar")
    .jPlayerId("playBar", "player_progress_play_bar")
    .jPlayerId("volumeMin", "player_volume_min")
    .jPlayerId("volumeMax", "player_volume_max")
    .jPlayerId("volumeBar", "player_volume_bar")
    .jPlayerId("volumeBarValue", "player_volume_bar_value")
    .onProgressChange( function(loadPercent, playedPercentRelative, playedPercentAbsolute, playedTime, totalTime) {
	var myPlayedTime = new Date(playedTime);
	var ptMin = (myPlayedTime.getUTCMinutes() < 10) ? "0" + myPlayedTime.getUTCMinutes() : myPlayedTime.getUTCMinutes();
	var ptSec = (myPlayedTime.getUTCSeconds() < 10) ? "0" + myPlayedTime.getUTCSeconds() : myPlayedTime.getUTCSeconds();
	$("#play_time").text(ptMin+":"+ptSec);
	var myTotalTime = new Date(totalTime);
	var ttMin = (myTotalTime.getUTCMinutes() < 10) ? "0" + myTotalTime.getUTCMinutes() : myTotalTime.getUTCMinutes();
	var ttSec = (myTotalTime.getUTCSeconds() < 10) ? "0" + myTotalTime.getUTCSeconds() : myTotalTime.getUTCSeconds();
	$("#total_time").text(ttMin+":"+ttSec);
    })
    .onSoundComplete( function() {
	playlist_next();
	refresh_playlist();
    });
    $("#ctrl_prev").click( function() {
	playlist_prev();
	return false;
    });
    $("#ctrl_next").click( function() {
	playlist_next();
	return false;
    });
    display_playlist();
}
function display_playlist_element(item)
{
    $("#playlist_list ul").append("<li id='playlist_item_"+item.idx+"'><img src='/images/music/remove.png' class='remove_ icon' onclick='remove_from_playlist("+item.file_id+")' /> "+ item.name +"</li>");
    $("#playlist_item_"+item.idx).data( "index", item.idx ).hover(
	function()
	{
	    if (play_item != $(this).data("index"))
	    {
		$(this).addClass("playlist_hover");
	    }
	},
	function()
	{
	    $(this).removeClass("playlist_hover");
	}
    ).click(
	function(event)
	{
	    if (event.target.tagName.toLowerCase() == 'img')
		return false;
	    var index = $(this).data("index");
	    if (play_item != index)
	    {
		playlist_change(index);
	    }
	    else
	    {
		$("#jquery_jplayer").play();
	    }
	}); 
}
function display_playlist()
{
    if (play_list.length > 0)
    {
	for (i=0; i < play_list.length; i++)
	{
	    display_playlist_element(play_list[i]);
	}
    }
}

function playlist_init(autoplay)
{
    if (play_list.length > 0)
    {
	if(autoplay)
	{
	    playlist_change(0);
	}
	else
	{
	    playlist_config(0);
	}
    }
    else
    {
	play_item = -1;
    }
}
function playlist_config(index)
{
    if (play_item != -1)
    {
	$("#playlist_item_"+playlist_index[play_item]).removeClass("playlist_current");
    }
    $("#playlist_item_"+index).addClass("playlist_current");
    var item = play_list[index];
    play_item = item.file_id;
    if (item.ext == 'mp3')
    {
	jplayer.setFile(item.path);
    }
    else
    {
	jplayer.setFile('', item.path);
    }
    return jplayer;
}
function playlist_change(index)
{
    playlist_config(index).play();
}
function playlist_next()
{
    var index = (playlist_index[play_item] + 1 < play_list.length) ? playlist_index[play_item] + 1 : 0;
    playlist_change(index);
}
function playlist_prev()
{
    var index = (playlist_index[play_item] - 1 >= 0) ? playlist_index[play_item] - 1 : play_list.length - 1;
    playlist_change(index);
}

function add_to_playlist(item)
{
    play_list.push(item);
    reindex_playlist();
    var idx = item.idx;
    display_playlist_element(play_list[idx]);
    if (play_item == -1)
    {
	playlist_change(idx);
    }
    $.ajax({
	url: '/api/playlist/add/' + item.file_id,
	    dataType: 'json',
	    timeout: 1000,
	    success: function(response) 
	    {
		return response;
	    }
    });
    return idx;
}
function reindex_playlist()
{
    if (play_list.length > 0)
    {
	for (i=0; i < play_list.length; i++)
	{
	    play_list[i].idx = i;
	    playlist_index[play_list[i].file_id] = i;
	}
    }    
}
function refresh_playlist()
{
    $.ajax({
	url: '/api/playlist',
	dataType: 'json',
	timeout: 1000,
	success: function(response) 
	{
	    play_list = response;
	    $("#playlist_list ul").empty();
	    if (play_list.length == 0)
	    {
		jplayer.stop();
		return false;
	    }
	    reindex_playlist();
	    if (playlist_index[play_item] == null)
	    {
		play_item = play_list[0].file_id;
		playlist_config(0);
	    }
	    display_playlist();
	    $("#playlist_item_"+playlist_index[play_item]).addClass("playlist_current");
	    return response;
	}
    });    
}
function remove_from_playlist(file_id)
{
    var item = playlist_index[file_id];
    $("#playlist_item_"+item.idx).remove();
    if (play_item == file_id)
    {
	playlist_next();
    }
    $.ajax({
	url: '/api/playlist/remove/' + file_id,
	dataType: 'json',
	timeout: 1000,
	success: function(response) 
	{
	    refresh_playlist();
	}
    });
    reindex_playlist();
}
function play_at_playlist(item)
{
    var idx = add_to_playlist(item);
    if (play_item != item.file_id)
    {
	playlist_change(idx);
    }
}