# -*- coding: utf-8 -*-
<%page args="filter" />
<form method="POST"/>
<table style="border:1px #000000 solid;">
<tr>
  <td>${_('Filters')}</td>
  <td>${_('Sorting')}</td>
</tr>
<tr>
<td id='filter-td'>
  %for f in filter.filters:
  <div><input type="hidden" name="filter" value="${f[0]}:${f[1]}"/> ${f[0]} ${f[1]} [<a onclick="remove_filter_element(this);">X</a>]</div>
  %endfor
</td>
<td id='sort-td'>
  %for s in filter.sort:
  <div><input type="hidden" name="sort" value="${s[0]}:${s[1]}"/> ${s[0]} ${s[1]} [<a onclick="remove_filter_element(this);">X</a>]</div>
  %endfor
</td>
</tr>
<tr>
  <td>
    <script>
      var filter_values = {
      '':'',
      %for f in filter.base.filters:
      '${f}':['${"', '".join(filter.base.filters[f][2])}'],
      %endfor
      };
    </script>
    <select id='filter-add' onchange="change_filter_values(this);">
      <option></option>
      %for f in filter.base.filters:
      <option>${f}</option>
      %endfor
    </select>
    <select id='filter-add-value'></select>
    <input type="button" value="${_('Add')}" onclick="add_filter_element(this, 'filter')"/>
  </td>
  <td>
    <select id='sort-add'>
      %for s in filter.base.sort:
      <option>${s}</option>
      %endfor
    </select>
    <select id='sort-add-value'><option>asc</option><option>desc</option></select>
    <input type="button" value="${_('Add')}" onclick="add_filter_element(this, 'sort')"/>
  </td>
</tr>
<tr>
<td colspan="2">
${'Total entries'}: ${filter.total}, ${_('show entries per page')}: <select name="per_page"><option>${filter.per_page}</option><option>10</option><option>20</option><option>25</option><option>50</option><option>100</option></select> <input type="submit" value="${_('Apply')}" />
</td>
</tr>
</table>
</form>
