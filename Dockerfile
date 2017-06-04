FROM        stibbons31/alpine-s6-python3-twisted:py3.6-tx17.1
MAINTAINER  gaetan@xeberon.net

# set environment variables
ENV         PYTHONIOENCODING="UTF-8"
ARG         DEBIAN_FRONTEND="noninteractive"

RUN         apk add --no-cache --update \
                    curl \
                    git

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

# clean up
RUN         rm -rf \
                /root/.cache \
                /tmp/*


# Docker configuration
EXPOSE      8086
VOLUME      /animes /movies /tv
