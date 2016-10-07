
function countdown() {
  var seconds = 30;
  var counter = $("#counter")[0];

  function tick() {
    seconds--;
    counter.innerHTML = "0:" + (seconds < 10 ? "0" : "") + String(seconds);
    if( seconds > 0 ) {
        setTimeout(tick, 1000);
    } else {
      var submit = $("#submit")[0];
      submit.click();
    }
  }
  if(counter) {
    tick();
  }
}

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
    socket.send(JSON.stringify({
      'action': 'slider',
      "sliderValue": ui.value
    }));
  }
});
$('.ui-slider-handle').hide();

function set_breadcrumbs(state, round){
  $("#"+state).addClass("active");
  $("#currentRound").html(round);
  // remove all other active classes
  // set current roud
  console.log(state);
}

$(function () {

  var ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
  var ws_path = ws_scheme + '://' + window.location.host + "/multiplayer/lobby/";

  console.log("Connecting to " + ws_path);
  socket = new ReconnectingWebSocket(ws_path);

  // Helpful debugging
  socket.onopen = function () {
    console.log("Connected to chat socket");
  };

  socket.onclose = function () {
    console.log("Disconnected from chat socket");
  };

  socket.onmessage = function (msg) {
    var data = JSON.parse(msg.data);
    data.action = 'interactive';

    if(data.error){
      console.log(data.msg);
      return;
    }

    if(data.action == "info"){
      document.querySelector('#waiting').innerHTML = data.text;
    }
    else if(data.action == "redirect"){
      var proto = ws_scheme == "wss" ? "https://" : "http://";
      window.location.href = proto + window.location.host + data.url;
    }
    else if(data.action == 'initial'){
      state = 'initial';
      $("#lobby").hide();
      $("#breadcrumbs").show();
      set_breadcrumbs(state, data.current_round);
      $("#game").show();
      $("img.img-responsive").attr("src", '/static/plots/' + data.plot);
      countdown();
      $("#remaining").html(data.remaining);
    }
    else if(data.action == 'ping'){
      console.log(data.text)
    }
    else if(data.action == 'interactive'){
      state = 'interactive';
      $("#lobby").hide();
      $("#breadcrumbs").show();
      set_breadcrumbs(state, data.current_round);
      $("#game").show();
      $("img.img-responsive").attr("src", '/static/plots/' + data.plot);
      countdown();
      $("#remaining").html(data.remaining);

      $("#interactiveGuess").show();

      data.following = [{"user":"Test", "avatar":"cow.png", "score": 1.0}]
      console.log(data.following);

      // for(var i = 0; i < data.following.length(); i++) {
      //   var user = data.following[i];
      //    <td><img src={% static 'images/avatars/'+user.avatar %} class="avatar" /> 100
      //       </td>
      // }
      // $('#picker').style.display = 'block';
      // $('#lobby').style.display = 'none';
      // $('#game').style.display = 'block';
      // $('#breadcrumbs').style.display = 'block';
      // $('#socialGuess').className = 'active';
      // $('.interactive').style.display = 'block';
      // $All('.follow').forEach(function (elem) {
      //     elem.style.display = 'none';
      // });
      // $('img.img-responsive').src = '/static/plots/' + data.plot;
      // $('#remaining').innerHTML = 'Plots remaining: ' + data.remaining;
      // console.log(data.current_round);
      // console.log(data.following)
      /*
       *
       *  'plot': round_data.get('plot'),
       * 'remaining': round_data.get('remaining'),
       * 'current_round': round_data.get('current_round'),
       * # a list of dicts of {usernames and avatars} for the players that the user follows
       * 'following': following,
       *
       * */

      // countdown();
    }
    else if(data.action == 'outcome'){
        state = 'outcome';
        reset_breadcrumbs();
        $('#lobby').style.display = 'none';
        $('#game').style.display = 'block';
        $('#breadcrumbs').style.display = 'block';
        $('#outcome').className = 'active';
        $('.interactive').style.display = 'block';
        $('#picker').style.display = 'none';
        $('.interactive').style.display = 'none';
        $All('.follow').forEach(function (elem) {
            elem.style.display = 'block';
        });

        /*
         *
         * 'plot': round_data.get('plot'),
         * 'remaining': round_data.get('remaining'),
         * 'current_round': round_data.get('current_round'),
         * # a list of dicts of {username, avatar, score} for the players that the user follows
         * 'following': following,
         * 'all_players': users,
         *
         * */


        // countdown();
    }
    else if(data.action == 'SliderChange'){
        /*
         *
         * 'username': user.username,
         * 'slider': slider,
         *
         * */
        console.log('User: ' + data.username);
        console.log('slider value: ' + data.slider)

    }
    else if(data.action == 'followNotify'){
        /*
         *
         * 'following': follow_users,
         *
         * */
        console.log('Following list: ' + data.following_users)

    }
    else{
        console.log(data)
    }
  };
});


$('#submit').click(function () {
   if (state == 'initial'){
       var guess = document.querySelector('#guess').value;
       socket.send(JSON.stringify({
           action: 'initial',
           guess: guess
       }));
   }
   else if(state == 'interactive'){
        var socialGuess = document.querySelector('#guess').value;
        socket.send(JSON.stringify({
            action: 'interactive',
            socialGuess: socialGuess
        }))
   }
   else{
       console.log(state)
   }
});
