FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    libpq-dev postgresql postgresql-contrib\
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONUNBUFFERED 1

WORKDIR /django-app

COPY . /django-app

RUN pip install --upgrade pip

RUN pip install -r requirements.txt

RUN python manage.py collectstatic --noinput

EXPOSE 8000