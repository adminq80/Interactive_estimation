/* Project specific Javascript goes here. */
function countdown() {
  var seconds = 30;
  var counter = $("#counter")[0];

  function tick() {
    seconds--;
    counter.innerHTML = "0:" + (seconds < 10 ? "0" : "") + String(seconds);
    if(seconds > 0) {
      setTimeout(tick, 1000);
      if(seconds == 10) {
        $("#counter").css("color", "red");
        $("#counter").css("font-size", "26px");
      }
    } else {
      var submit = $("#submit")[0];
      $("#submit").removeAttr("disabled");
      submit.click();
    }
  }
  if(counter) {
    tick();
  }
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
    $('#slider > .ui-slider-handle').show();
    $("#submit").removeAttr("disabled");
    $('#guess').val(ui.value);
  }
});

$('#slider > .ui-slider-handle').hide();

