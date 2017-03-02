from channels import include, route

from game.interactive_shocks.consumers import game_watcher, kickout

channel_routing = [
    include('game.interactive_shocks.routing.websocket_routing', path=r'^/dynamic_mode/lobby'),
    include('game.interactive_static.routing.websocket_routing', path=r'^/static_mode/lobby'),
    route('delayed_task', game_watcher),
    route('kickout', kickout),
]
