from channels import route
from .consumers import exit_game, lobby, ws_receive
from .consumers import cancel_game, data_broadcast, follow_list, initial_submit, interactive_submit, \
    reset_timer, round_outcome


game_routes = [
    route('game.route', initial_submit, action='^initial$'),  # initial guess submission
    route('game.route', data_broadcast, action='^slider$'),  # broadcast guess to player
    route('game.route', interactive_submit, action='^interactive$'),
    route('game.route', follow_list, action='^follow$'),
    route('game.route', round_outcome, action='^outcome$'),
    route('game.route', reset_timer, action='^resetTimer$'),
    route('game.route', cancel_game, action='^exit_game$'),
]


websocket_routing = [
    route('websocket.connect', lobby),  # , path=r'^/multiplayer/lobby/$'),
    route('websocket.disconnect', exit_game),
    route('websocket.receive', ws_receive),
] + game_routes
