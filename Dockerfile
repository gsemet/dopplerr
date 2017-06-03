FROM        stibbons31/alpine-s6-python3:latest
MAINTAINER  gaetan@xeberon.net

# set environment variables
ENV         PYTHONIOENCODING="UTF-8"
ARG         DEBIAN_FRONTEND="noninteractive"
ENV         XDG_CONFIG_HOME="/config/xdg"

# install build packages
RUN         apk add --no-cache --virtual=build-dependencies \
                    autoconf \
                    automake \
                    freetype-dev \
                    g++ \
                    gcc \
                    jpeg-dev \
                    lcms2-dev \
                    libffi-dev \
                    libpng-dev \
                    libwebp-dev \
                    linux-headers \
                    make \
                    openjpeg-dev \
                    openssl-dev \
                    python3-dev \
                    tiff-dev \
                    zlib-dev

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
RUN         apk del --purge \
                build-dependencies \
        &&  rm -rf \
                /root/.cache \
                /tmp/*


# Docker configuration
EXPOSE      8086
VOLUME      /animes /movies /tv
