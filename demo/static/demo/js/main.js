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
    controls: false,
    nextSelector: '#slider-next',
    prevSelector: '#slider-prev',
    nextText: '',
    prevText: '',
    auto: 'true',
  });
  var button = $('#mobile_menu_button'), menuItems = $('.mobileMenuItem'), menuSize = 0;

  menuSize = 15 + ($(menuItems).length * 40);

  console.log(menuSize);

  $(button).click(function(){
        if (button.hasClass('inactive')) {
            $(".mobileMenuContainer").height(menuSize);
            button.removeClass('inactive').removeClass('fa-bars').addClass('fa-times-circle');
        }
        else {
            $(".mobileMenuContainer").height('0px');
            button.addClass('inactive').addClass('fa-bars').removeClass('fa-times-circle');
        }
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

