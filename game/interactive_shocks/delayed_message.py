from django.db import transaction
from channels import Channel

from .models import Task


class DelayedMessageExecutor:

    def __init__(self, content: dict, milliseconds: int):
        with transaction.atomic():
            t = Task(**content)
            t.save()
        delayed_message = {
            'channel': 'delayed_task',
            'content': {'task': t.id},
            'delay': milliseconds * 1000,
        }
        self.message = delayed_message

    def send(self, immediately=True):
        with transaction.atomic():
            Channel('asgi.delay').send(self.message, immediately=immediately)
