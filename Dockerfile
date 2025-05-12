# Dockerfile
# sudo docker build -t pushingkarma -f Dockerfile .
# sudo docker run pushingkarma --name pushingkarma -d -p 8080:80/tcp -v /volume1/docker/pushingkarma:/app:rw
FROM python:3.12-slim
RUN apt-get update
RUN apt-get install -y build-essential cron nginx supervisor
RUN rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY pyproject.toml .
COPY docker/nginx.conf /etc/nginx/sites-enabled/pushingkarma
COPY docker/supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY docker/crontab.conf /etc/cron.d/pushingkarma

RUN pip install uv
RUN uv pip install -r pyproject.toml
RUN echo 'daemon off;' >> /etc/nginx/nginx.conf
CMD supervisord

