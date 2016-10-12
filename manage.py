#!/usr/bin/env python
import os
import sys

from channels.asgi import get_channel_layer

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
    channel_layer = get_channel_layer()

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
