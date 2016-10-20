$(document).ready(function(){
  $(".overview-1 > .row > .nextButton").click(function() {
    $(".overview-1").hide();
    $(".overview-2").show();
  })
  $(".overview-2 > .row > .nextButton").click(function() {
    $(".overview-2").hide();
    $(".overview-3").show();
  })
  $(".overview-3 > .row > .nextButton").click(function() {
    $(".overview-3").hide();
    $(".overview-4").show();
  })
  $(".overview-4 > .row > .nextButton").click(function() {
    $(".overview-4").hide();
    $(".overview-5").show();
  })

  $(".overview-2 > .row > .prevButton").click(function() {
    $(".overview-2").hide();
    $(".overview-1").show();
  })
  $(".overview-3 > .row > .prevButton").click(function() {
    $(".overview-3").hide();
    $(".overview-2").show();
  })
  $(".overview-4 > .row > .prevButton").click(function() {
    $(".overview-4").hide();
    $(".overview-3").show();
  })
  $(".overview-5 > .row > .prevButton").click(function() {
    $(".overview-5").hide();
    $(".overview-4").show();
  })

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

});

