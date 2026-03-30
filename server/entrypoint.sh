#!/bin/sh
set -e

echo "Applying Django migrations"
python manage.py migrate --noinput

echo "Collecting static files"
python manage.py collectstatic --noinput

exec "$@"
