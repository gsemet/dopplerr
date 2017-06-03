FROM        stibbons31/alpine-s6-python3:latest
MAINTAINER  gaetan@xeberon.net

# set environment variables
ENV         PYTHONIOENCODING="UTF-8"
ARG         DEBIAN_FRONTEND="noninteractive"
ENV         XDG_CONFIG_HOME="/config/xdg"

RUN         apk add --no-cache --update \
                    curl \
                    git \
                    py3-twisted

# copy containers's startup files
COPY        root/ /
RUN         mkdir -p /media

# Injecting files into containers
RUN         mkdir -p /app
COPY        . /app
WORKDIR     /app

# Building python application
RUN         ./bootstrap.sh
RUN         cd /app \
        &&  ./install.sh system

# Docker configuration
EXPOSE      8086
VOLUME      /animes /movies /tv
