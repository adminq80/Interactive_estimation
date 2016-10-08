
function countdown(counterState) {
  var counter = $('#counter');
  var seconds = 30;

  function tick() {
    if(counterState == state) {
      seconds--;
      counter[0].innerHTML = "0:" + (seconds < 10 ? "0" : "") + String(seconds);
      if( seconds > 0 ) {
        setTimeout(tick, 1000);
      } else {
        var submit = $("#submit")[0];
        submit.click();
      }
    }
  }
  tick();
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

function set_breadcrumbs(state, round) {
  var breadcrumbs = $("#breadcrumbs > ul").children();
  $.each(breadcrumbs, function(i, item) {
    $(item).removeClass("active");
  })
  $("#"+state).addClass("active");
  $("#currentRound").html(round);
}

function start_game(data) {
  state = data.action;
  $("#lobby").hide();
  $("#breadcrumbs").show();
  set_breadcrumbs(state, data.current_round);
  $("#game").show();
  $("img.img-responsive").attr("src", '/static/plots/' + data.plot);
  countdown(state);
  $("#remaining").html(data.remaining);
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
    // data.action = 'outcome'; //testing

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
      start_game(data);
    }
    else if(data.action == 'ping'){
      console.log(data.text)
    }
    else if(data.action == 'interactive'){
      start_game(data);

      $("#interactiveGuess").show();

      data.following = [{"username":"Test", "avatar":"cow.png", "score": 1.0}]
      $.each(data.following, function(i, user) {
        var avatar = "/static/images/avatars/"+user.avatar;
        $("#following_list tbody").append(`
          <tr>
            <td id=${user.username}>
              <img src=${avatar} class='avatar' />
              <span>${user.score}</span>
            </td>
          </tr>
        `);
      })
    }
    else if(data.action == 'outcome'){
      start_game(data);

      $(".outcome").show();

      // populate list of people you can follow
      data.all_players = [{"username":"Test", "avatar":"cow.png", "score": 1.0}];
      $.each(data.all_players, function(i, user) {
        var avatar = "/static/images/avatars/"+user.avatar;
        $("#follow_list").append(`
          <div class="user" id=${user.username}>
            <img src="/static/images/plus.ico" class="plusIcon" />
            <img src=${avatar} class="avatar" /> ${user.score}
          </div>
        `);
      })

      // popular list of people you can unfollow
      data.following = [{"username":"Test", "avatar":"pig.png", "score": 1.0}];
      $.each(data.following, function(i, user) {
        var avatar = "/static/images/avatars/"+user.avatar;
        $("#unfollow_list tbody").append(`
          <tr>
            <td id=${user.username}>
              <img src=${avatar} class='avatar' />
              <span>${user.score}</span>
              <button type="button" class="btn btn-primary unfollow">Unfollow</button>
            </td>
          </tr>
        `);
      })

      $(".plusIcon").click(function(e) {
        var username = e.target.parentElement.id;
      });

      $(".unfollow").click(function(e) {
        var username = e.target.parentElement.id; 
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
    }
    else if(data.action == 'sliderChange'){
      $(`#${data.username} > span`).html(data.slider);
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
  // show window "Waiting for others to submit..."
  if (state == 'initial') {
    console.log("TEST");
    var guess = $('#guess');
    console.log(guess);
    socket.send(JSON.stringify({
      action: 'initial',
      guess: guess,
      payload: {action: "interactive"}
    }));
    // socket.send(JSON.stringify({action:"initial", payload:{plot:"0.png", action:"interactive"}}));
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
