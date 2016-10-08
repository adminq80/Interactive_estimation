from django.http import HttpResponse

from channels import Group
from channels.handler import AsgiHandler


#def ws_message(message):
#    message.reply_channel.send({
#        "text": message.content['text'],
#    })


def home(message):
    response = HttpResponse("Hello world! You asked for %s" % message.content['path'])
    for chunk in AsgiHandler.encode_response(response):
        message.reply_channel.send(chunk)


# Connected to websocket.connect
def ws_add(message):
    Group("chat").add(message.reply_channel)


# Connected to websocket.disconnect
def ws_disconnect(message):
    Group("chat").discard(message.reply_channel)


# Connected to websocket.receive
def ws_message(message):
    Group("chat").send({
        "text": "[user] %s" % message.content['text'],
    })

