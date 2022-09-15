FROM python:3.10.5-slim-bullseye

ENV CELERY_BROKER_URL redis://redis:6379/0
ENV CELERY_RESULT_BACKEND redis://redis:6379/0
ENV C_FORCE_ROOT true

ENV HOST 0.0.0.0
ENV PORT 5001
ENV DEBUG true

COPY . /app
WORKDIR /app

RUN apt-get update && apt-get install --no-install-recommends -y \
    gcc libc-dev libpq-dev python-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
RUN pip install -U setuptools pip
RUN pip install -r requirements.txt

EXPOSE 5001
