FROM python:3.11

#
WORKDIR /app

#
COPY ./requirements.txt /app/requirements.txt
COPY . /app/
#
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt


RUN chmod +x ./docker/entrypoints/django-entrypoint.sh

