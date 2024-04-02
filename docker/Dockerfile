# Dockerfile
#
# == Build regular ==
# docker build -t pushingkarma -f docker/Dockerfile .
#
# == Build arm64 ==
# docker buildx create --use
# docker buildx build --platform linux/arm64 -t pushingkarma_arm64 -f docker/Dockerfile .
# docker save -o pushingkarma_arm64.tar pushingkarma_arm64
# scp -O pushingkarma.tar synology:~
# ssh synology
# > docker load -i pushingkarma_arm64.tar
# > docker run -d -p 80:80 pushingkarma_arm64
FROM python:3.11
WORKDIR /app
RUN apt-get update && apt-get install -y build-essential curl libbz2-dev \
  libffi-dev liblzma-dev libncursesw5-dev libreadline-dev libsqlite3-dev \
  libssl-dev libxml2-dev libxmlsec1-dev llvm make python3-dev tk-dev wget \
  xz-utils zlib1g-dev redis-server nginx supervisor
COPY ../. .
COPY docker/nginx.conf /etc/nginx/sites-enabled/default
COPY docker/secrets.py /app/pk/settings/secrets.py
COPY docker/supervisord.conf /etc/supervisor/conf.d/supervisord.conf
RUN pip install -r /app/pk/requirements.pip
RUN echo 'daemon off;' >> /etc/nginx/nginx.conf
CMD supervisord
