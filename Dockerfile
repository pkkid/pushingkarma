# Dockerfile
# Docker container used to run the website with
# daphne, nginx, and cron via supervisord 
FROM python:3.12-slim
RUN apt-get update
RUN apt-get install -y bash build-essential ca-certificates cron curl git nginx supervisor
RUN rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY pyproject.toml .
COPY docker/nginx.conf /etc/nginx/sites-enabled/pushingkarma.conf
COPY docker/supervisord.conf /etc/supervisor/conf.d/pushingkarma.conf
COPY docker/crontab.conf /etc/cron.d/pushingkarma

RUN pip install uv
RUN uv venv /opt/venv
RUN /opt/venv/bin/python -m ensurepip
RUN VIRTUAL_ENV=/opt/venv uv pip install -r pyproject.toml

# Install Claude Code CLI from the official installer.
RUN curl -fsSL https://claude.ai/install.sh | bash

RUN echo 'daemon off;' >> /etc/nginx/nginx.conf
CMD rm -f /tmp/daphne.sock.lock && supervisord

