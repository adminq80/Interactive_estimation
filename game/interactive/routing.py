from channels import route
from .consumers import data_submit, exit_game, lobby, send_data
from .consumers import data_broadcast, follow_list, unfollow


data_routing = [
    route('data.initial', data_submit),  # initial guess submission
    route('data.broadcast', data_broadcast)  # broadcast guess to player
]

followers = [
    route('follow.list', follow_list),
    route('unfollow', unfollow)
]


websocket_routing = [
    route('websocket.connect', lobby),
    route('websocket.disconnect', exit_game),
    route('websocket.receive', send_data),

] + data_routing + followers
