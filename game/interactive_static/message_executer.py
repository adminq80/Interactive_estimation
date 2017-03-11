from django.db import transaction
from channels import Channel

from .models import Task


class DelayedMessageExecutor:

    def __init__(self, content: dict, seconds: float):
        with transaction.atomic():
            t = Task(**content)
            t.save()
        delayed_message = {
            'channel': 'static_delayed_task',
            'content': {'task': t.id},
            'delay': int(seconds * 1000),
        }
        self.message = delayed_message

    def send(self, immediately=True):
        Channel('asgi.delay').send(self.message, immediately=immediately)
