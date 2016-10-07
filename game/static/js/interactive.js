
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

function reset_breadcrumbs(){
    document.querySelector('#yourGuess').className = '';
    document.querySelector('#socialGuess').className = '';
    document.querySelector('#outcome').className = '';
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
            state = 'initial';
            reset_breadcrumbs();
            document.querySelector('#picker').style.display = 'block';
            document.querySelector('#lobby').style.display = 'none';
            document.querySelector('#game').style.display = 'block';
            document.querySelector('#breadcrumbs').style.display = 'block';
            document.querySelector('#yourGuess').className = 'active';
            document.querySelectorAll('.follow').forEach(function (elem) {
                elem.style.display = 'none';
            });
            document.querySelector('.interactive').style.display = 'none';
            document.querySelector('img.img-responsive').src = '/static/plots/' + data.plot;
            document.querySelector('#remaining').innerHTML = 'Plots remaining: ' + data.remaining;
            /*
             *
             * The available data are plot, remaining and current_round
             * */
            console.log(data.plot);
            console.log(data.remaining);
            console.log(data.current_round);

            // countdown();
        }
        else if(data.action == 'ping'){
            console.log(data.text)
        }
        else if(data.action == 'interactive'){
            state = 'interactive';
            reset_breadcrumbs();
            document.querySelector('#picker').style.display = 'block';
            document.querySelector('#lobby').style.display = 'none';
            document.querySelector('#game').style.display = 'block';
            document.querySelector('#breadcrumbs').style.display = 'block';
            document.querySelector('#socialGuess').className = 'active';
            document.querySelector('.interactive').style.display = 'block';
            document.querySelectorAll('.follow').forEach(function (elem) {
                elem.style.display = 'none';
            });
            document.querySelector('img.img-responsive').src = '/static/plots/' + data.plot;
            document.querySelector('#remaining').innerHTML = 'Plots remaining: ' + data.remaining;
            console.log(data.current_round);
            console.log(data.following)
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
            document.querySelector('#lobby').style.display = 'none';
            document.querySelector('#game').style.display = 'block';
            document.querySelector('#breadcrumbs').style.display = 'block';
            document.querySelector('#outcome').className = 'active';
            document.querySelector('.interactive').style.display = 'block';
            document.querySelector('#picker').style.display = 'none';
            document.querySelector('.interactive').style.display = 'none';
            document.querySelectorAll('.follow').forEach(function (elem) {
                elem.style.display = 'block';
            });

            /*
             *
             * 'plot': round_data.get('plot'),
             * 'remaining': round_data.get('remaining'),
             * 'current_round': round_data.get('current_round'),
             * # a list of dicts of {usernames and avatars} for the players that the user follows
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
