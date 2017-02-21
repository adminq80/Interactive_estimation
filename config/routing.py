from channels import include

channel_routing = [
    include('game.interactive_shocks.routing.websocket_routing', path=r'^/dynamic_mode/lobby'),
    include('game.interactive_static.routing.websocket_routing', path=r'^/static_mode/lobby'),
]
