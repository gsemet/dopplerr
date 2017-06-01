FROM    jfloff/alpine-python:3.4-slim
MAINTAINER gaetan@xeberon.net

RUN     apk add --update curl git

RUN     mkdir -p /app
COPY    . /app
WORKDIR /app

RUN     ./bootstrap.sh
RUN     cd /app \
     && ./install.sh prod

RUN     mkdir -p /media

EXPOSE  8000
CMD     ["pipenv", "run", "python", "/app/proxy.py", "-p 8000", "-a /app"]
