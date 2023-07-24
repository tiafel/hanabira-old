function add_filter_element(obj, t)
{
    var param = $('#'+t+'-add').val();
    var value = $('#'+t+'-add-value').val();
    $('#'+t+'-td').append(
	'<div><input type="hidden" name="' + t + '" value="' +param+ ':' +value+ '"/> '+param+' '+value+' [<a onclick="remove_filter_element(this);">X</a>]</div>'
	);
}    
function remove_filter_element(obj)
{
    $(obj).parent().remove();
}

function change_filter_values(obj)
{
    var param = $('#filter-add').val();
    var sel2 = $('#filter-add-value');
    sel2.empty();
    if (param)
    {
	for (val in filter_values[param])
	{
	    sel2.append("<option>" + filter_values[param][val] + "</option>");
	}
    }
}
   