var jcrop_api = null;
function show_preview(coords)
{
	var ry = 200 / coords.h;
	//var rx = coords.w * ry;
    $('#jcrop-preview-div').css({
	width: Math.round(ry * coords.w) + 'px'
    });
    $('#jcrop-preview').css({
	width: Math.round(ry * image_width) + 'px',
	height: Math.round(ry * image_height) + 'px',
	marginLeft: '-' + Math.round(ry * coords.x) + 'px',
	marginTop: '-' + Math.round(ry * coords.y) + 'px'
    });
    $('#x').val(coords.x);
    $('#y').val(coords.y);
    $('#w').val(coords.w);
    $('#h').val(coords.h);
    $('#shi-width').val(coords.w);
    $('#shi-height').val(coords.h);
}
$(function(){
    jcrop_api = $.Jcrop('#jcrop-image', {
	onChange: show_preview,
	onSelect: show_preview,
	aspectRatio: 4/3,
    });
    init_motivator();
});
function init_motivator()
{
    $('#motivator-options').show();
    $('#aspect1').attr('checked','checked');
    $('#jcrop-preview-div').css({
	border: '20px solid #000000',
	borderBottom: '50px solid #000000'
    });
    jcrop_api.setOptions({aspectRatio: 4/3});
    jcrop_api.setSelect([0, 0, image_width, image_height]);
}
function init_macro()
{
    $('#macro-options').show();
    jcrop_api.setOptions({aspectRatio: 0});
    jcrop_api.setSelect([0, 0, image_width, image_height]);
}
function init_shi()
{
    $('#shi-options').show();
    jcrop_api.setOptions({aspectRatio: 0});
    jcrop_api.setSelect([0, 0, image_width, image_height]);
}
function update_aspect(opt)
{
    var ar = 0;
    if (opt.value == 'landscape')
    {
	ar = 4/3;
    }
    if (opt.value == 'portrait')
    {
	ar = 3/4;
    }
    jcrop_api.setOptions({aspectRatio: ar});
    jcrop_api.focus();
}
function update_tool(e, obj)
{
    $('#motivator-options').hide();
    $('#macro-options').hide();
    $('#shi-options').hide();
    $('#jcrop-preview-div').css({
	border: '',
    });
    if (obj.value == 'motivator')
    {
	init_motivator();
    }
    else if (obj.value == 'macro')
    {
	init_macro();
    }
    else
    {
	init_shi();
    }
    return true;
}
