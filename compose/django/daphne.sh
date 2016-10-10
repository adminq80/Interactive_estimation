#!/bin/sh
python /app/manage.py collectstatic --noinput



daphne config.asgi:channel_layer -b 0.0.0.0 -p 5000 --root-path=/app




