#!/bin/sh
set -e

echo "Waiting for postgres at ${POSTGRES_HOST}:${POSTGRES_PORT}..."
until pg_isready -h "${POSTGRES_HOST}" -p "${POSTGRES_PORT}" -U "${POSTGRES_USER}" >/dev/null 2>&1; do
  sleep 1
done

python manage.py migrate --noinput
python manage.py collectstatic --noinput
python manage.py seed_demo_data

if [ "$#" -eq 0 ]; then
  exec python manage.py runserver 0.0.0.0:8000
else
  exec "$@"
fi
