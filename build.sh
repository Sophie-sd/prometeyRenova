#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
python manage.py makemessages -l uk -l en
python manage.py compilemessages
python manage.py collectstatic --no-input
python manage.py migrate