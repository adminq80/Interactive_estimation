from channels import route
from .consumers import exit_game, lobby


websocket_routing = [
    route('websocket.connect', lobby),
    route('websocket.disconnect', exit_game),

]
