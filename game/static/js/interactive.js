//timer
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

function new_follow_list(name, avatar, score) {
  $("#follow_list").append(`
    <div class="user" id=${name}>
      <img src="/static/images/plus.ico" class="plusIcon" />
      <img src=${avatar} class="avatar" /> <span class="userScore">Score: ${score}</span>
    </div>
  `);
}

function new_unfollow_list(name, avatar, score) {
  return (`
    <img src=${avatar} class='avatar' />
    <span>Score: ${score}</span>
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
  $('.ui-slider-handle').hide();
  $('#guess').val(-1);
  $('#correlation')[0].innerHTML = '';
}

function start_game(data) {
  state = data.action;
  $("#myModal").modal('hide');
  $("#lobby").hide();
  set_breadcrumbs(state, data.current_round);
  $("#game").show();

  $("img.img-responsive").attr("src", '/static/plots/' + data.plot);
  countdown(state);
  $("#remaining").html(data.remaining);

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
    row.html(new_unfollow_list(user.username, avatar, user.score));
  });

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
      resetSlider();

      $(".guess").show();
      $(".outcome").hide();

      if(data.current_round == 0) {
        // plays bell at start of game
        var audio = new Audio('/static/bell.mp3');
        audio.play();
      }

    }
    else if(data.action == 'ping'){
      console.log(data.text)
    }
    else if(data.action == 'interactive'){

      start_game(data);
      $(".guess").show();

      $("#interactiveGuess").show();

      // data.following = [{"username":"Test", "avatar":"cow.png", "score": 1.0}]
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
            </td>
          </tr>
        `);
      })
    }
    else if(data.action == 'outcome'){

      $("#unfollow_list tbody").html("");

      for(var i = 0; i < data.max_following; i++) {
        $("#unfollow_list tbody").append("<tr><td></td></tr>");
      }

      start_game(data);
      $("#interactiveGuess").hide();
      $(".guess").hide();
      $(".outcome").show();
      $("#yourGuess").html(data.guess);
      $("#roundAnswer").html(data.correct_answer);

      start_interactive(data);

      following = data.following.map(function(user) {
        return user.username;
      });

      $(document).on("click", ".plusIcon", function(e) {
        var username = e.target.parentElement.id;
        var avatar = $(`div#${username}>.avatar`).attr('src');
        var score = $(`div#${username}>.userScore`).html();

        var followingCopy = following.slice();
        followingCopy.push(username);

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
      $(`#${data.username} > span`).html(data.slider);
    }
    else if(data.action == 'followNotify'){
      following = data.following.map(function(user) {
        return user.username;
      });
      start_interactive(data);
    }
    else{
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
