#!/bin/sh
python manage.py migrate
python manage.py rundelay &
python manage.py runserver 0.0.0.0:8000
