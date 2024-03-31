# Dockerfile
FROM python:3.11
WORKDIR /app
RUN apt-get update && apt-get install -y build-essential curl libbz2-dev \
  libffi-dev liblzma-dev libncursesw5-dev libreadline-dev libsqlite3-dev \
  libssl-dev libxml2-dev libxmlsec1-dev llvm make python3-dev tk-dev wget \
  xz-utils zlib1g-dev redis-server nginx
COPY ../pk/requirements.pip .
RUN pip install -r requirements.pip
COPY ../. .
COPY docker/nginx.conf /etc/nginx/sites-enabled/default
EXPOSE 80
CMD service redis-server start && \
  daphne -u /app/pk/daphne.sock pk.asgi:application && \
  service nginx start
  
