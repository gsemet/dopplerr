FROM        stibbons31/alpine-s6-python3-twisted:py3.6-tx17.9
MAINTAINER  gaetan@xeberon.net

# set environment variables
ENV         PYTHONIOENCODING="UTF-8"
ARG         DEBIAN_FRONTEND="noninteractive"

RUN         apk add --no-cache --update \
                    curl \
                    git \
                    gcc \
                    python3-dev \
                    make \
                    linux-headers \
                    musl-dev \
                    nodejs

# Injecting files into containers
RUN         mkdir -p /app
WORKDIR     /app

# Keep dependencies on its own Docker FS Layer
# To avoid dependencies reinstall at each code change
COPY        Pipfile* setup-pip.sh /app/
RUN         ./setup-pip.sh \
        &&  pipenv install --system

# Adding rest of the application in next docker layers
COPY        . /app/

# build frontend
RUN         apk add --no-cache --update \
                    nodejs \
                    nodejs-npm \
        &&  npm install -g npm@5

RUN         cd /app/frontend \
        &&  make dev \
        &&  make build \
        &&  mkdir -p /frontend \
        &&  cp -rf dist/ /frontend/ \
        &&  rm -rf /app/frontend

RUN         npm cache clear --force \
        &&  apk del \
                    nodejs \
                    nodejs-npm

# installing main Python module to system
RUN         cd /app \
        &&  pip install .

# copy containers's startup files
COPY        root/ /
RUN         mkdir -p /media

USER        root
# clean up
RUN         apk del \
                    python3-dev \
                    make \
                    gcc \
                    curl \
                    linux-headers \
                    musl-dev \
                    nodejs  \
        &&  rm  -rf \
                /root/.cache \
                /tmp/*

# Docker configuration
EXPOSE      8086
VOLUME      /config \
            /animes \
            /movies \
            /tv
