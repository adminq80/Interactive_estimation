from channels import route
from .consumers import exit_game, lobby, ws_receive
from .consumers import data_broadcast, initial_submit, interactive_submit, round_outcome


game_routes = [
    # route('initial.guess', initial_submit),  # initial guess submission
    # route('slider.change', data_broadcast),  # broadcast guess to player
    # route('interactive.guess', interactive_submit),
    # route('follow.list', follow_list),
    # todo: creating a route for next round

    route('game.route', initial_submit, action='^initial$'),  # initial guess submission
    route('game.route', data_broadcast, action='^slider$'),  # broadcast guess to player
    route('game.route', interactive_submit, action='^interactive$'),
    # route('game.route', follow_list, action='^follow$'),
    route('game.route', round_outcome, action='^outcome$'),

]


websocket_routing = [
    route('websocket.connect', lobby),  # , path=r'^/multiplayer/lobby/$'),
    route('websocket.disconnect', exit_game),
    route('websocket.receive', ws_receive),

    # route('websocket.connect', lobby2, path='^/some/$'),
] + game_routes
