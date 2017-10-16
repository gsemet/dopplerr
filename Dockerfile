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
                    musl-dev

# copy containers's startup files
COPY        root/ /
RUN         mkdir -p /media

# Injecting files into containers
RUN         mkdir -p /app

# Keep dependencies on its own Docker FS Layer
# To avoid dependencies reinstall at each code change
COPY        Pipfile* /app
RUN         pipenv install
COPY        . /app

WORKDIR     /app

# Building python application
RUN         ./bootstrap-system.sh

RUN         cd /app \
        &&  make install-system


# clean up
RUN         apk del python3-dev \
                make \
                gcc \
                curl \
                linux-headers \
                musl-dev \
        &&  rm  -rf \
                /root/.cache \
                /tmp/*

# Docker configuration
EXPOSE      8086
VOLUME      /config /animes /movies /tv
