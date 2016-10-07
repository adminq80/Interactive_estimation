import logging
import json
from functools import wraps

from django.conf import settings


def channel_debugger(func):
    name = func.__name__

    @wraps(func)
    def inner(message, *args, **kwargs):
        if settings.DEBUG:
            print(name)
            logging.info(name)
            payload = message.content.get('payload')
            message.reply_channel.send({
                'text': json.dumps(payload)
            })
        func(message, *args, **kwargs)

    return inner
