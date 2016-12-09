from django.views.generic import TemplateView

from channels.routing import route, route_class

# from control.consumers import home, ws_message
# from game.control.consumers import home, ws_add, ws_disconnect, ws_message

from game.interactive.consumers import lobby

from channels import include

channel_routing = [
    include('game.interactive.routing.websocket_routing', path=r'^/multiplay/lobby'),
    include('game.interactive_shocks.routing.websocket_routing', path=r'^/multiplayer/lobby'),
    include('game.interactive_static.routing.websocket_routing', path=r'^/multiplay_game/lobby'),
    # # route('http.request', TemplateView.as_view(template_name='pages/home.html'), path=r'^/$', name='home'),
    #
    # # route("http.request", home),
    # # route("websocket.receive", ws_message),
    #
    #  route('websocket.connect', lo),
    #  route('websocket.receive', ws_message),
    #  route('websocket.disconnect', ws_disconnect),

]
