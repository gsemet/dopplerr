FROM    jfloff/alpine-python:3.4-slim

RUN     apk add --update curl
RUN     pip install pipenv

RUN     mkdir -p /app
ADD     . /app
WORKDIR /app

RUN     cd /app \
     && pipenv install .

RUN     cd /app \
     && curl -L https://github.com/ebergama/sonarr-sub-downloader/archive/v0.4.zip \
             -o sonarr-sub-downloader.zip \
     && unzip -o sonarr-sub-downloader.zip

EXPOSE  8000
CMD     ["pipenv", "run", "python", "/app/proxy.py", "-p 8000", "-a /app"]
