$(document).ready(function() {
  for(let i = 1; i < 8; i++) {

    $(`.overview-${i} > .row > .nextButton`).click(function() {
      $(`.overview-${i}`).hide();
      $(`.overview-${i+1}`).show();
    })
  }

  for(let i = 2; i < 7; i++) {
    $(`.overview-${i} > .row > .prevButton`).click(function() {
      $(`.overview-${i}`).hide();
      $(`.overview-${i-1}`).show();
    })

  }
  $(".overview-7 > form >  .row > .prevButton").click(function(){
     $(`.overview-7`).hide();
      $(`.overview-6`).show();
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
    console.log(j);
    for(var i = 1; i<8; i++){
      $(`.overview-${i}`).hide();
    }
    $(`.overview-${j}`).show();
  }
  else {
    $(".overview-1").show();
  }
});