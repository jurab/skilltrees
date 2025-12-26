#!/bin/bash
python manage.py collectstatic --noinput
python manage.py migrate
gunicorn skilltrees.wsgi --bind 0.0.0.0:${PORT:-8000}
