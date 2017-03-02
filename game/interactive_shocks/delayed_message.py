from django.db import transaction
from channels import Channel


class DelayedMessage:

    def __init__(self, channel, content: dict, milliseconds):
        delayed_message = {
            'channel': channel,
            'content': content,
            'delay': milliseconds * 1000,
        }
        self.message = delayed_message

    def send(self, immediately=True):
        print(self.message)
        with transaction.atomic():
            Channel('asgi.delay').send(self.message, immediately=immediately)
