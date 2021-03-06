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

function class_name_for_score(group){
    if (group === '1')
    return 'high-gain';
  if (group === '2')
      return 'medium-gain';
  return'low-gain';
}

function new_follow_list(name, avatar, score, round_score, group, disconnected) {
  var class_color = class_name_for_score(group);
  if(disconnected == null){
    $("#follow_list").append(`
    <div class="user" id=${name}>
      <a href="#" data-toggle="tooltip" data-placement="right" class="toolTip" title="Unfollow a user first">
        <img src="/static/images/plus.ico" class="plusIcon" />
      </a>
      <img src=${avatar} class="avatar" /> 
      <span style="white-space: nowrap">
      <span class="userScore">${score}</span> (<b class="${class_color}">+${round_score}</b>) <img id="coin" src="/static/images/coin.png" />
      </span>
    </div>
  `);
  }else{
    $("#follow_list").append(`
    <div class="user" id=${name}>
      <a href="#" data-toggle="tooltip" data-placement="right" class="toolTip" title="Unfollow a user first">
        <img src="/static/images/plus.ico" class="plusIcon" />
      </a>
      <span style="white-space: nowrap">
      <img src=${avatar} class="avatar" /> 
      <span>(Disconnected!)</span></span>
    </div>`);
  }
}

function new_unfollow_list(name, avatar, score, round_score, group, disconnected) {
  var class_color = class_name_for_score(group);
  if(disconnected == null){
   return (`
    <img src=${avatar} class='avatar' />
    <span style="white-space: nowrap">
    <span>${score}</span> (<b class="${class_color}">+${round_score}</b>) <img id="coin" src="/static/images/coin.png" />
    </span>
    <button type="button" id=${name} class="btn btn-primary unfollow">Unfollow</button>
  `);
  }
  return (`
    <span style="white-space: nowrap">
    <img src=${avatar} class='avatar' />
    <span>(Disconnected!)</span>
    </span>
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
  });
  $("#"+state).addClass("active");
  $("#currentRound").html(round);
}

function resetSlider() {
  $('#slider > .ui-slider-handle').hide();
  $('#guess').val(-1);
  $('#correlation')[0].innerHTML = '';
}

function round_sound(){
  var audio = new Audio('/static/round-sound.mp3');
  audio.play();
}
function start_game(data, seconds) {
  state = data.action;
  $("#myModal").modal('hide');
  $("#submit").removeClass("highlight");
  $("#submitText").addClass("hide");
  $("#lobby").hide();
  set_breadcrumbs(state, parseInt(data.current_round) + 1);
  $("#game").show();

  $("img.img-responsive").attr("src", '/static/plots/' + data.plot);
  countdown(state, seconds);
  $("#remaining").html(parseInt(data.remaining) + parseInt(data.current_round));
  $(".user_score").html(data.score);
  round_sound();

}

function comp_score(a, b) {
  try {
    var a_score = parseFloat(a.score) || parseFloat(JSON.parse(sessionStorage.getItem(a.username)).score);
    var b_score = parseFloat(b.score) || parseFloat(JSON.parse(sessionStorage.getItem(b.username)).score);
  }
  catch (e){
    return 1;
  }
  return a_score >= b_score ? -1: 1;
}

function start_interactive(data) {
  // populate list of people you can follow
  $("#follow_list").html("");
  var arr = JSON.parse(sessionStorage.getItem('disconnected')) || [];
  var all_players = data.all_players;
  var following = data.following;
  $.each(all_players.sort(comp_score), function(i, user) {
    var avatar = '/static/' + user.avatar;
    var user_data = JSON.parse(sessionStorage.getItem(user.username));
    console.log('follow');
    console.log(user_data);
    new_follow_list(user.username, avatar, parseFloat(user_data.score), parseFloat(user_data.gain), user_data.batch,
        arr.find(function(i){return i == user.username}));
  });
  $("#unfollow_list tbody td").html("");
  // populate list of people you can unfollow
  $.each(following.sort(comp_score), function(i, user) {
    var avatar = "/static/"+user.avatar;
    var user_data = JSON.parse(sessionStorage.getItem(user.username));
    console.log('unfollow');
    console.log(user_data);
    var row = $($("#unfollow_list tbody td")[i]);
    row.html(new_unfollow_list(user.username, avatar, parseFloat(user_data.score), parseFloat(user_data.gain), user_data.batch,
        arr.find(function(i){return i == user.username})));
  });
}

function start_initial(data){
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



function percentile_generator(data){
      var all_users = [];
      $.each(data.following, function(i, user){
        all_users.push(user);
      });
      $.each(data.all_players, function(i, user){
        all_users.push(user);
      });
      all_users.push({username:"self", gain:data.gain || 0, score: data.score || 0});
    var batch = Math.floor(all_users.length / 3);
    $.each(all_users.sort(function(a, b){return parseFloat(a.gain) > parseFloat(b.gain) ? -1:1;}), function (i, user) {
      var d = {gain: user.gain || 0, score: user.score || 0};
      if(i < batch) {
        d.batch = '1';
       }else if (i < (batch<<1)){
        d.batch = '2';
       }else{
         d.batch = '3';
       }
       sessionStorage.setItem(user.username, JSON.stringify(d));
    });
}

function start_outcome(data){
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
      if(data.guess > -1) {
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
          $($("#answerSlider > .ui-slider-handle")[0]).addClass("true-answer");
        }
        else {
          $($("#answerSlider > .ui-slider-handle")[1]).addClass("true-answer");
        }
      }
      else {
        $("#yourGuess").html('N/A');
        $("#answerSlider").slider({
          min: 0,
          max: 1,
          step: 0.01,
          value: data.correct_answer,
          disabled: true
        });
        $($("#answerSlider > .ui-slider-handle")[0]).addClass("true-answer");
      }

      $("#roundAnswer").html(data.correct_answer);
      $("#roundBonus").html('+' + data.gain);

      if (window.location.pathname.match(/dynamic_mode/)) {
          percentile_generator(data);
          var user_data = JSON.parse(sessionStorage.getItem('self'));
          $('#user_round_score').html('+' + data.gain);
          $('#user_round_score2').removeClass('high-gain medium-gain low-gain').addClass(class_name_for_score(user_data.batch));
          $('#user_round_score').removeClass('high-gain medium-gain low-gain').addClass(class_name_for_score(user_data.batch));
          $('#roundBonus').removeClass('high-gain medium-gain low-gain').addClass(class_name_for_score(user_data.batch));
      }

      $(".img-responsive").addClass("faded");

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

$(function () {
  var ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
  var path = window.location.pathname == "/static_mode/lobby/" ? "/static_mode/lobby/": "/dynamic_mode/lobby/";
  game_type = window.location.pathname == "/static_mode/lobby/" ? "static": "dynamic";
  var ws_path = ws_scheme + '://' + window.location.host + path;
  socket = new ReconnectingWebSocket(ws_path);
  sessionStorage.clear();

  if (!socket){
    alert("Your browser doesn't support Websocket");
  }

  socket.onopen = function () {
    $( "#dialog-confirm" ).dialog({
      autoOpen: false,
        resizable: false,
        height: "auto",
        width: 400,
        modal: true,
        buttons: {
        "Remain in lobby": function(){
          $( this ).dialog( "close" );
          clearInterval(sound_player);
          socket.send(JSON.stringify({action:'resetTimer'}));
        },
        Exit: function(){
          $( this ).dialog( "close" );
          clearInterval(sound_player);
          socket.send(JSON.stringify({action:'exit_game'}));
        }
      }
    });
  };

  socket.onclose = function () {
  };

  socket.onmessage = function (msg) {
    var data = JSON.parse(msg.data);
    if(data.error){
      console.log(data.msg);
      return;
    }
    console.log(data.action);

    if(data.action == "info"){
      document.querySelector('#connected_players').innerHTML = data.connected_players || 0;
      document.querySelector('#total_players').innerHTML = data.total_players || 0;
      round_sound();
    }
    else if(data.action == "redirect"){
      var proto = (ws_scheme == "wss") ? "https://" : "http://";
      window.location.href = proto + window.location.host + data.url;
    }
    else if(data.action == 'avatar'){
      $('.user-avatar').attr('src', data.url);
      $('.user-avatar-large').attr('src', data.url);
    }
    else if(data.action == 'initial') {
      start_initial(data);
    }
    else if(data.action == 'ping'){
      console.log(data.text)
    }
    else if(data.action == 'interactive') {
      start_game(data, data.seconds);
      $(".guess").show();

      $("#interactiveGuess").show();
      $(".box#score").html(`${data.score}`);

      $("#following_list tbody").html("");

      $.each(data.following.sort(comp_score), function(i, user) {
        if (user.guess == null || user.guess == -1) {
          user.guess = null;
        }
        var avatar = "/static/"+user.avatar;
        var arr = JSON.parse(sessionStorage.getItem('disconnected')) || [];
        if(arr.find(function(u){return u == user.username})){
          $("#following_list tbody").append(`
          <tr>
            <td id=${user.username} style="white-space: nowrap">
              <img src=${avatar} class='avatar' />
              <span>(Disconnected!)</span>
            </td>
          </tr>
        `);
          return;
        }
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

        if (user.guess == null) {
          $(`td#${user.username} > span`).html('');
          $(`td#${user.username} > .followingSlider > .ui-slider-handle`).hide();
        }
        else {
          $(`td#${user.username} > .followingSlider`).slider( "option", "value", user.guess);
        }
      })
    }
    else if(data.action == 'outcome'){
      start_outcome(data);
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
    else if(data.action == 'logout'){
      console.log("logout");
      window.location.href = data.url;
    }
    else if(data.action == 'AFK'){
      clearInterval(sound_player);
      window.location.href = 'http://acronym.wikia.com/wiki/AFK';
    }
    else if(data.action == 'disconnected'){
      console.log(data.username);
      //noinspection JSDuplicatedDeclaration
        var arr = JSON.parse(sessionStorage.getItem('disconnected')) || [];
      arr.push(data.username);
      sessionStorage.setItem('disconnected', JSON.stringify(arr));
    }
    else if (data.action == 'reconnected'){
      console.log('User '+ data.username + 'recoonected !');
      //noinspection JSDuplicatedDeclaration
        var arr = JSON.parse(sessionStorage.getItem('disconnected')) || [];
      sessionStorage.setItem('disconnected', JSON.stringify(arr.filter(function(i){ return i !== data.username;})));
    }
    else if (data.action = 'timeout_prompt'){
      console.log('Timeout');
      if(data.minutes !== null){
        $('#waiting_time').html(data.minutes + ' minutes')
      }
      else{
        $('#waiting_time').html(data.seconds + ' seconds')
      }
      sound_player = setInterval(round_sound, data.sound_interval*1000);
      round_sound();
      $( "#dialog-confirm" ).dialog( "open" );
    }
    else {
      console.log(data.action);
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
  }
});
