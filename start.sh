#!/bin/bash
python manage.py collectstatic --noinput
python manage.py migrate
gunicorn skilltrees.wsgi
