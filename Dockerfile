FROM       lsiobase/alpine.python:3.6
MAINTAINER gaetan@xeberon.net

# set environment variables
ENV        PYTHONIOENCODING="UTF-8"
ARG        DEBIAN_FRONTEND="noninteractive"
ENV        XDG_CONFIG_HOME="/config/xdg"

RUN        apk add --update curl git
RUN        apk del python2 \
                   py-setuptools \
                   py2-pip
RUN        apk add python3 \
                   py3-pip \
                   python3-dev \
                   py3-setuptools \
                   py3-twisted

# copy containers's startup files
COPY       root/ /
RUN        mkdir -p /media

# Injecting files into containers
RUN        mkdir -p /app
COPY       . /app
WORKDIR    /app

# Building python application
RUN        ./bootstrap.sh
RUN        cd /app \
        && ./install.sh docker

# Docker configuration
EXPOSE     8086
VOLUME     /animes /movies /tv
