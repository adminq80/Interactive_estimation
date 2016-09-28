from channels import route
from .consumers import exit_game, lobby, send_data



websocket_routing = [
    route('websocket.connect', lobby),
    route('websocket.disconnect', exit_game),
    route('websocket.receive', send_data),
]
