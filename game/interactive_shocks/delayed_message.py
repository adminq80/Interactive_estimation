import json
from channels import Channel


class DelayedMassage:

    def __init__(self, channel, content: dict, milliseconds):
        delayed_message = {
            'channel': channel,
            'content': content,
            'delay': milliseconds * 1000,
        }
        self.channel = channel
        self.content = content
        self.seconds = milliseconds * 1000
        self.message = delayed_message

    def send(self, immediately=True):
        Channel('asgi.delay').send(self.message, immediately=immediately)
