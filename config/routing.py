from channels import include, route

from game.interactive_shocks.consumers import task_runner

channel_routing = [
    include('game.interactive_shocks.routing.websocket_routing', path=r'^/dynamic_mode/lobby'),
    include('game.interactive_static.routing.websocket_routing', path=r'^/static_mode/lobby'),
    route('delayed_task', task_runner),
]
