$(function() {
	$('#slider').nivoSlider();
	$('.lightbox').lightBox();
	var border200 = '<img src="images/gallery_border_200.png" alt="photo" width="200" height="144" border="0" class="galleryborder"/>';
	var border300 = '<img src="images/photo_300_border.png" alt="border" width="300" height="214" class="image_right_border" />';
	$('.grunge_border_200').each(function(){
		if($('a',this).length > 0){
			$('a',this).prepend(border200);
		}else{
			$(this).prepend(border200);
		}
	});
	$('.grunge_border_300').each(function(){
		if($('a',this).length > 0){
			$('a',this).prepend(border300);
		}else{
			$(this).prepend(border300);
		}
	});
	$('#home_buttons .fade').fadeOut('fast');
	$('#home_buttons li').hover(function(){
		$('.fade',this).fadeIn();
	},function(){
		$('.fade',this).fadeOut();
		});
});