$(document).ready(function() {
  for(let i = 1; i <= 5; i++) {
    $(`.overview-${i} > .row > .nextButton`).click(function() {
      $(`.overview-${i}`).hide();
      $(`.overview-${i+1}`).show();
    })
  }

  for(let i = 2; i <= 6; i++) {
    $(`.overview-${i} > .row > .prevButton`).click(function() {
      $(`.overview-${i}`).hide();
      $(`.overview-${i-1}`).show();
    })
  }

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

