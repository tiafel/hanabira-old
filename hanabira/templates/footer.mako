<br/>
<p class="footer">
    - hanabira ${app_globals.settings.dist.version} + <a href="http://wakaba.c3.cx/">wakaba</a> + <a href="http://www.1chan.net/futallaby/">futallaby</a> + <a href="http://www.2chan.net/">futaba</a> -
    ${c.pageinfo.lower_banner |n}
</p>

%if app_globals.settings.chan.debug and c.sum:
<br/>	Total time: ${c.sum} <br/><br/>
%endif

%if app_globals.settings.chan.debug and c.log:
<font size="-2">
  %for l in c.log:
    ${l}<br/><br/>
  %endfor
</font>
%endif

