$(document).ready(function() {
  var upperBound = document.location.pathname.match(/solo/) == null ? 7: 6;
  for(let i = 1; i <= upperBound; i++) {

    $(`.overview-${i} > .row > .nextButton`).click(function() {
      $(`.overview-${i}`).hide();
      $(`.overview-${i+1}`).show();
    })
  }

  for(let i = 2; i < upperBound; i++) {
    $(`.overview-${i} > .row > .prevButton`).click(function() {
      $(`.overview-${i}`).hide();
      $(`.overview-${i-1}`).show();
    })

  }
  $(`.overview-${upperBound} > form >  .row > .prevButton`).click(function(){
     $(`.overview-${upperBound}`).hide();
      $(`.overview-${upperBound-1}`).show();
  });

  $(".submitButton").click(function() {
    $(".answer").html("0.87");
  })

  $("#sampleSlider").slider({
    min: 0,
    max: 1,
    step: 0.01,
    slide: function(event, ui) {
      $('#correlation')[0].innerHTML = ui.value;
    },
    change: function(event, ui) {
      $('.ui-slider-handle').show();
    }
  });

  $('.ui-slider-handle').hide();

  if (document.location.hash){
    var j = +document.location.hash.replace(/#overview-([1-7])/, '$1');
    for(var i = 1; i <= upperBound; i++){
      $(`.overview-${i}`).hide();
    }
    $(`.overview-${j}`).show();
  }
  else {
    $(".overview-1").show();
  }
});