//timer
function countdown(counterState, s) {
  var counter = $('#counter');
  var seconds = s || 30;

  function tick() {
    if(counterState == state) {
      seconds--;
      counter[0].innerHTML = "0:" + (seconds < 10 ? "0" : "") + String(seconds);
      if( seconds > 0 ) {
        setTimeout(tick, 1000);
        if(seconds == 10) {
          $("#counter").css("color", "red");
          $("#counter").css("font-size", "32px");
        }
      } else {
        var submit = $("#submit")[0];
        $("#submit").removeAttr("disabled");
        submit.click();
      }
    }
  }
  $("#counter").css("color", "#006400");
  $("#counter").css("font-size", "28px");
  tick();
}

function new_follow_list(name, avatar, score) {
  $("#follow_list").append(`
    <div class="user" id=${name}>
      <a href="#" data-toggle="tooltip" data-placement="right" class="toolTip" title="Unfollow a user first">
        <img src="/static/images/plus.ico" class="plusIcon" />
      </a>
      <img src=${avatar} class="avatar" /> 
      <span class="userScore">${score} </span><img id="coin" src="/static/images/coin.png" />
    </div>
  `);
}

function new_unfollow_list(name, avatar, score, round_score) {
  return (`
    <img src=${avatar} class='avatar' />
    <span>${score} </span> (+${round_score}) <img id="coin" src="/static/images/coin.png" />
    <button type="button" id=${name} class="btn btn-primary unfollow">Unfollow</button>
  `);
}
//slider
$("#slider").slider({
  min: 0,
  max: 1,
  step: 0.01,
  slide: function(event, ui) {
    $('#correlation')[0].innerHTML = ui.value;
    socket.send(JSON.stringify({
      'action': 'slider',
      "sliderValue": ui.value
    }));
  },
  change: function(event, ui) {
    $('#slider > .ui-slider-handle').show();
    $('#guess').val(ui.value);
    $("#submitText").removeClass("hide");
    $("#submit").removeAttr("disabled");
    $("#submit").addClass("highlight");
  }
});

//breadcrumbs
function set_breadcrumbs(state, round) {
  $("#breadcrumbs").show();
  var breadcrumbs = $("#breadcrumbs > ul").children();
  $.each(breadcrumbs, function(i, item) {
    $(item).removeClass("active");
  })
  $("#"+state).addClass("active");
  $("#currentRound").html(round);
}

function resetSlider() {
  $('#slider > .ui-slider-handle').hide();
  $('#guess').val(-1);
  $('#correlation')[0].innerHTML = '';
}

function start_game(data, seconds) {
  state = data.action;
  $("#myModal").modal('hide');
  $("#submit").removeClass("highlight");
  $("#submitText").addClass("hide");
  $("#lobby").hide();
  set_breadcrumbs(state, data.current_round);
  $("#game").show();

  $("img.img-responsive").attr("src", '/static/plots/' + data.plot);
  countdown(state, seconds);
  $("#remaining").html(data.remaining);
  $(".user_score").html(data.score);

  var audio = new Audio('/static/round-sound.mp3');
  audio.play();

}

function start_interactive(data) {

  // populate list of people you can follow
  $("#follow_list").html("");
  $.each(data.all_players, function(i, user) {
    var avatar = '/static/' + user.avatar;
    new_follow_list(user.username, avatar, user.score);
  });

  $("#unfollow_list tbody td").html("");
  // populate list of people you can unfollow
  $.each(data.following, function(i, user) {
    var avatar = "/static/"+user.avatar;
    var row = $($("#unfollow_list tbody td")[i]);
    row.html(new_unfollow_list(user.username, avatar, user.score, user.round_score));
  });

}


$(function () {

  var ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
  var path = null;
  if(window.location.pathname == '/multiplay/lobby/'){
    path = "/multiplay/lobby/";
  }
  else if (window.location.pathname == '/multiplayer/lobby/') {
    path = "/multiplayer/lobby/";
  }
  else{
    path = '/multiplay_game/lobby/';
  }
  var ws_path = ws_scheme + '://' + window.location.host + path;

  // console.log("Connecting to " + ws_path);
  socket = new ReconnectingWebSocket(ws_path);

  if (!socket){
    console.log('Socket is null');
    alert("Your browser doesn't support Websocket");
  }

  // Helpful debugging
  socket.onopen = function () {
    console.log("Connected to chat socket");
  };

  socket.onclose = function () {
    console.log("Disconnected from chat socket");
  };

  socket.onmessage = function (msg) {
    // console.log(msg.data);
    var data = JSON.parse(msg.data);

    if(data.error){
      console.log(data.msg);
      return;
    }

    if(data.action == "info"){
      document.querySelector('#connected_players').innerHTML = data.connected_players || 0;
      document.querySelector('#total_players').innerHTML = data.total_players || 0;
    }
    else if(data.action == "redirect"){
      var proto = (ws_scheme == "wss") ? "https://" : "http://";
      window.location.href = proto + window.location.host + data.url;
    }
    else if(data.action == 'avatar'){
      $('.user-avatar').attr('src', data.url);
    }
    else if(data.action == 'initial') {
      $(".img-responsive").removeClass("faded");

      start_game(data, data.seconds);
      resetSlider();

      $(".guess").show();
      $(".outcome").hide();

      if(data.current_round == 0) {
        var audio = new Audio('/static/bell.mp3');
        audio.play();
      }

    }
    else if(data.action == 'ping'){
      console.log(data.text)
    }
    else if(data.action == 'interactive') {
      console.log(data);
      start_game(data, data.seconds);
      $(".guess").show();

      $("#interactiveGuess").show();
      $(".box#score").html(`${data.score}`);

      $("#following_list tbody").html("");
      $.each(data.following, function(i, user) {
        if (user.guess < 0) {
          user.guess = '';
        }
        var avatar = "/static/"+user.avatar;
        $("#following_list tbody").append(`
          <tr>
            <td id=${user.username}>
              <img src=${avatar} class='avatar' />
              <span>${user.guess}</span>
              <div class="followingSlider"></div>
            </td>
          </tr>
        `);

        $(`td#${user.username} > .followingSlider`).slider({
          min: 0,
          max: 1,
          step: 0.01,
          disabled: true
        });

        if (user.guess == '') {
          $(`td#${user.username} > .followingSlider > .ui-slider-handle`).hide();
        }
        else {
          $(`td#${user.username} > .followingSlider`).slider( "option", "value", user.guess);
        }
      })
    }
    else if(data.action == 'outcome'){
      console.log('data', data);
      
      $(".box#score").html(`${data.score}`);
      $("#unfollow_list tbody").html("");

      for(var i = 0; i < data.max_following; i++) {
        $("#unfollow_list tbody").append("<tr><td></td></tr>");
      }

      start_game(data, data.seconds);
      $("#interactiveGuess").hide();
      $(".guess").hide();
      $(".outcome").show();
      $("#yourGuess").html("");

      // this is going to be an answer slider
      $("#answerSlider").html("");
      if(data.guess != -1) {
        $("#yourGuess").html(data.guess);
        $("#answerSlider").slider({
          range: true,
          min: 0,
          max: 1,
          step: 0.01,
          values: [data.correct_answer, data.guess].sort(),
          disabled: true
        });
        if(data.guess > data.correct_answer) {
          $($("#answerSlider > .ui-slider-handle")[0]).css("background-color", "green");
        }
        else {
          $($("#answerSlider > .ui-slider-handle")[1]).css("background-color", "green");
        }
      }
      else {
        console.log("reset slider");
        $("#answerSlider").slider({
          range: true,
          min: 0,
          max: 1,
          step: 0.01,
          value: data.correct_answer,
          disabled: true
        });
        $($("#answerSlider > .ui-slider-handle")[0]).css("background-color", "green");
      }
      $("#roundAnswer").html(data.correct_answer);
      // to be replaced 

      $(".img-responsive").addClass("faded");


      // TO-DO add user's round_bonus to the data
      // $("#roundBonus").html(data.round_bonus);


      start_interactive(data);

      following = data.following.map(function(user) {
        return user.username;
      });

      if(following.length == data.max_following) {
        $('[data-toggle="tooltip"]').tooltip();
      }

      $(document).on("click", ".plusIcon", function(e) {
        var username = e.target.parentElement.parentElement.id;

        var followingCopy = following.slice();
        followingCopy.push(username);
        $('[data-toggle="tooltip"]').tooltip('hide');
        socket.send(JSON.stringify({
          action: 'follow',
          following: followingCopy
        }));
      });


      $(document).on("click", ".unfollow", function(e) {

        var username = e.target.id;
        var toRemove = following.indexOf(username);
        var followingCopy = following.slice();
        followingCopy.splice(toRemove, 1);
        socket.send(JSON.stringify({
          action: 'follow',
          following: followingCopy
        }));

      });

    }
    else if(data.action == 'sliderChange'){
      $(`td#${data.username} > span`).html(data.slider);
      $(`td#${data.username} > .followingSlider > .ui-slider-handle`).show();
      $(`td#${data.username} > .followingSlider`).slider( "option", "value", data.slider);
    }
    else if(data.action == 'followNotify'){
      following = data.following.map(function(user) {
        return user.username;
      });
      start_interactive(data);
    }
    else {
      console.log(data)
    }
  };
});

$('input#submit').click(function () {
  $("#myModal").modal('show');

  if (state == 'initial') {
    var guess = $('#guess').val();
    socket.send(JSON.stringify({
      action: 'initial',
      guess: guess
    }));
  }
  else if(state == 'interactive'){
    var guess = $('#guess').val();
    socket.send(JSON.stringify({
      action: 'interactive',
      socialGuess: guess
    }));
  }
  else if(state == 'outcome'){
    socket.send(JSON.stringify({
      action: 'outcome'
    }));
  }
  else {
     console.log(state)
  }
});
