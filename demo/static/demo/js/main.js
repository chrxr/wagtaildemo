$(document).ready(function(){
  $('.slider1').bxSlider({
/*    slideWidth: 640,*/
    minSlides: 1,
    maxSlides: 1,
    slideMargin: 10,
    captions: true,
    adaptiveHeight: true,
    mode: 'fade',
    pager: false,
    controls: true,
/*    nextSelector: '#slider-next',
    prevSelector: '#slider-prev',*/
  });
});

/*$(document).ready(function(){
    // Initialise bxSlider 
    $('.bxslider').bxSlider({
        captions: true,
        adaptiveHeight: true,
        mode: 'fade',
    });

    //Apply img-thumbnail class to body-content images
    $('.body-content img').addClass("img-thumbnail");
});*/