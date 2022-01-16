FROM python:3.10.1-slim

WORKDIR /api

ENV GUNICORN_CMD_ARGS="--bind=0.0.0.0:80 --workers=5 --log-file=/var/log/confapi/debug.log\
                       --access-logfile /var/log/confapi/access.log --log-level debug" \
    TZ='Europe/Moscow'

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN apt update -y

COPY app/ /api
COPY requirements.txt /api
COPY config.ini /api
COPY example_data.csv /api

RUN pip install -r requirements.txt
RUN mkdir /var/log/confapi
