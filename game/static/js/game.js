/* Project specific Javascript goes here. */

function countdown() {
  var seconds = 30;
  function tick() {
    var counter = $("#counter")[0];
    seconds--;
    counter.innerHTML = "0:" + (seconds < 10 ? "0" : "") + String(seconds);
    if( seconds > 0 ) {
        setTimeout(tick, 1000);
    } else {
      var submit = $("#submit")[0];
      submit.click();
    }
  }
  tick();
}
countdown();

$("#slider").slider({
  min: 0,
  max: 1,
  step: 0.01,
  slide: function(event, ui) {
    $('#correlation')[0].innerHTML = ui.value;
  },
  change: function(event, ui) {
    $('.ui-slider-handle').show();
    $('#guess').val(ui.value);
  }
});

$('.ui-slider-handle').hide();
