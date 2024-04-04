# Dockerfile
# sudo docker build -t pushingkarma -f Dockerfile .
# sudo docker run pushingkarma --name pushingkarma -d -p 8080:80/tcp -v /volume1/docker/pushingkarma:/app:rw
FROM python:3.11
WORKDIR /app
RUN apt-get update && apt-get install -y build-essential cron curl libbz2-dev libffi-dev \
  liblzma-dev libncursesw5-dev libreadline-dev libsqlite3-dev libssl-dev libxml2-dev \
  libxmlsec1-dev llvm make nginx python3-dev redis-server rustc supervisor tk-dev wget \
  xz-utils zlib1g-dev
COPY docker/nginx.conf /etc/nginx/sites-enabled/default
COPY docker/supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY pk/requirements.pip /tmp/requirements.pip
RUN pip install --no-binary :all: -r /tmp/requirements.pip
RUN echo 'daemon off;' >> /etc/nginx/nginx.conf
CMD supervisord
