#!/bin/sh
python /app/prod.py collectstatic --noinput
python manage.py rundelay &
python /app/prod.py runserver 0.0.0.0:5000

#python /app/manage.py runworker -v2 --only-channels=http.* &
#daphne -v2 config.asgi:channel_layer -b 0.0.0.0 -p 5000 --root-path=/app