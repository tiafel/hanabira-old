<script type="text/javascript">
  var play_list = ${c.playlist.export() |n};
</script>
<div id="jquery_jplayer"></div>
<div id="music_player" style="display:none;">
  <hr/>
  <div id="player_container">
    <ul id="player_controls">
      <li id="player_play">play</li>
      <li id="player_pause">pause</li>
      <li id="player_stop">stop</li>
      <li id="player_volume_min">min volume</li>
      <li id="player_volume_max">max volume</li>
      <li id="ctrl_prev">previous</li>
      <li id="ctrl_next">next</li>
    </ul>

    <div id="play_time"></div>
    <div id="total_time"></div>
    <div id="player_progress">
      <div id="player_progress_load_bar">
	<div id="player_progress_play_bar"></div>
      </div>
    </div>
    <div id="player_volume_bar">
      <div id="player_volume_bar_value"></div>
    </div>


  </div>
  <div id="playlist_list">
    <ul></ul>
  </div>
  <div id="jplayer_info"></div>
</div>