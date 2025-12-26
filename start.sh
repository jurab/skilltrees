#!/bin/bash
python manage.py migrate
gunicorn skilltrees.wsgi
