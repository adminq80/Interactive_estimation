/* Project specific Javascript goes here. */
 function updateCorrelation(value){
  var box = document.getElementById("correlation");
  box.innerHTML = value;
}

function countdown() {
  var seconds = 60;
  function tick() {
    var counter = document.getElementById("counter");
    seconds--;
    counter.innerHTML = "0:" + (seconds < 10 ? "0" : "") + String(seconds);
    if( seconds > 0 ) {
        setTimeout(tick, 1000);
    } else {
      counter.style.color = "#F00";
      var submit = document.getElementById("submit");
      submit.click();
    }
  }
  tick();
}

countdown();