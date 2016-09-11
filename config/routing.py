from django.views.generic import TemplateView

from channels.routing import route, route_class

# from control.consumers import home, ws_message
from game.control.consumers import home, ws_add, ws_disconnect, ws_message

channel_routing = [
    # route('http.request', TemplateView.as_view(template_name='pages/home.html'), path=r'^/$', name='home'),
    
    # route("http.request", home),
    # route("websocket.receive", ws_message),

     route('websocket.connect', ws_add),
     route('websocket.receive', ws_message),
     route('websocket.disconnect', ws_disconnect),

]
