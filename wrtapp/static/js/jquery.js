
$(document).ready(function(){
      
// Back to top mygtukas
 $(window).scroll(function(){

  // Mygtuką parodo po 100px
  var showAfter = 100;
  if ( $(this).scrollTop() > showAfter ) { 
   $('.back-to-top').fadeIn();
  } else { 
   $('.back-to-top').fadeOut();
  }
 });
 
 //Paspaudus ant evento scrollina į viršų
 $('.back-to-top').click(function(){
  $('html, body').animate({scrollTop : 0},800);
  return false;
 });

});
