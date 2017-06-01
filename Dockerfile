FROM lsiobase/alpine.python:3.6
MAINTAINER gaetan@xeberon.net

# set python to use utf-8 rather than ascii
ENV PYTHONIOENCODING="UTF-8"

RUN     apk add --update curl git

# copy containers's startup files
COPY    root/ /
RUN     mkdir -p /media

# Injecting files into containers
RUN     mkdir -p /app
COPY    . /app
WORKDIR /app

# Building python application
RUN     ./bootstrap.sh
RUN     cd /app \
     && ./install.sh docker

# Docker configuration
EXPOSE  8086
VOLUME /animes /movies /tv
