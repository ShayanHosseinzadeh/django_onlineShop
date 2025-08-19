#!/bin/bash -x

python manage.py collectstatic --noinput
python manage.py migrate

gunicorn config.asgi:application \
    -k uvicorn.workers.UvicornWorker \
    -b 0.0.0.0:8000 \
    --workers 4
