FROM    jfloff/alpine-python:3.4-slim

RUN     apk add --update curl

RUN     mkdir -p /app
ADD     . /app
WORKDIR /app

RUN     ./bootstrap.sh
RUN     cd /app \
     && ./install.sh prod

EXPOSE  8000
CMD     ["pipenv", "run", "python", "/app/proxy.py", "-p 8000", "-a /app"]
