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
      <img src=${avatar} class="avatar" /> <span class="userScore">${score}</span>
    </div>
  `);
}

function new_unfollow_list(name, avatar, score) {
  return (`
    <td id=${name}>
      <img src=${avatar} class='avatar' />
      <span>${score}</span>
      <button type="button" class="btn btn-primary unfollow">Unfollow</button>
    </td>
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
$('.ui-slider-handle').hide();

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
      $("#follow_list tbody").html("");
        $.each(data.following, function(i, user) {
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
      start_game(data);

      $("#interactiveGuess").hide();
      $(".guess").hide();
      $(".outcome").show();

      // populate list of people you can follow
      $("#follow_list").html("");
        // console.log(data.all_players);
        //all_players
      $.each(data.all_players, function(i, user) {
        var avatar = '/static/' + user.avatar;
        new_follow_list(user.username, avatar, user.score);
      });

      // populate list of people you can unfollow
      // add empty table rows if following less than the max number of followers
      $("#unfollow_list tbody").html("");
        // console.log(data.following);
        //following
      $.each(data.following, function(i, user) {
        var avatar = "/static/"+user.avatar;
        $("#unfollow_list tbody").append("<tr>"+new_unfollow_list(user.username, avatar, user.score)+"</tr>");
      });

      var following = data.following.map(function(user) {
        return user.username;
      });

      $(document).on("click", ".plusIcon", function(e) {
        var username = e.target.parentElement.id;
        var avatar = $(`div#${username}>.avatar`).attr('src');
        var score = $(`div#${username}>.userScore`).html();
        
        var newFollowing = new_unfollow_list(username, avatar, score);
        socket.send(JSON.stringify({
          action: 'follow',
          following: following + [username]
        }));

        var rows = $("#unfollow_list tbody").children();
        for(var i = 0; i < rows.length; i++) {
          var row = rows[i];
          if ($(row).children().html() == "") {
            $(row).html(newFollowing);
            $(`div#${username}`).html("");
            break;
          }
        }
      });


      $(document).on("click", ".unfollow", function(e) {
        var username = e.target.parentElement.id;
        var avatar = $(`td#${username}>.avatar`).attr('src');
        var score = $(`td#${username}>span`).html();

        var toRemove = following.indexOf(username);
        following.splice(toRemove, 1)

        socket.send(JSON.stringify({
          action: 'follow',
          following: following
        }));

        $(`td#${username}`).html("");
        new_follow_list(username, avatar, score);

      });

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
  $("#myModal").modal('show');

  console.log('Button at state = ' + state);

  if (state == 'initial') {
    var guess = $('#guess').val();
    socket.send(JSON.stringify({
      action: 'initial',
      guess: guess
      // payload: {action: "interactive"}
    }));
  }
  else if(state == 'interactive'){
    var guess = $('#guess').val();
    socket.send(JSON.stringify({
      action: 'interactive',
      socialGuess: guess
      // payload: {action: "outcome"}
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
