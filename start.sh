#!/bin/bash
python manage.py collectstatic --noinput
python manage.py migrate
python manage.py loaddata skills/fixtures/initial_data.json || true
gunicorn skilltrees.wsgi --bind 0.0.0.0:${PORT:-8000}
