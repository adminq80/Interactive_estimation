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
            message.reply_channel.send({
                'text': json.dumps({
                    'action': message.content.get('action') or 'ping',
                    'text': name,
                })
            })
        func(message, *args, **kwargs)

    return inner
