Dopplerr Subtitle Downloader
============================

[![Build Status](https://travis-ci.org/Stibbons/dopplerr.svg?branch=master)](https://travis-ci.org/Stibbons/dopplerr)
[![Docker Automated buil](https://img.shields.io/docker/build/stibbons31/dopplerr.svg)](https://hub.docker.com/r/stibbons31/dopplerr/builds/)
[![Pypi package](https://badge.fury.io/py/dopplerr.svg)](https://pypi.python.org/pypi/dopplerr/) [![PyPI](https://img.shields.io/pypi/pyversions/dopplerr.svg)](https://pypi.python.org/pypi/dopplerr/)
[![Coveralls](https://coveralls.io/repos/github/Stibbons/dopplerr/badge.svg)](https://coveralls.io/github/Stibbons/dopplerr)
[![codecov](https://codecov.io/gh/Stibbons/dopplerr/branch/master/graph/badge.svg)](https://codecov.io/gh/Stibbons/dopplerr)
[![Maintainability](https://api.codeclimate.com/v1/badges/62d3040e8e7f37e637bf/maintainability)](https://codeclimate.com/github/Stibbons/dopplerr/maintainability)
[![MIT licensed](https://img.shields.io/badge/license-MIT-blue.svg)](./LICENSE)

Subtitle Download Web Service for Sonarr or Radarr. It uses [Subliminal](https://github.com/Diaoul/subliminal) to search automatically for missing subtitles on download notification.

-   Free software: MIT
-   Source: <https://github.com/Stibbons/dopplerr>
-   Python 3.
-   Docker image based on Alpine Linux and S6-Overlay (based on
    [Linuxserver](https://www.linuxserver.io/)'s images)

Usage
-----

The best usage is through the docker image.

### Limitations

- only Sonarr notification
- video filename should not have been renamed
- season folder might exist, or not
- all series should be on the same root directory
- exact series title folder (no year, no extra)

### Use with Docker

Use my docker image:

    docker create \
        --name dopplerr \
        -p 8086:8086 \
        -e PUID=<UID> \
        -e PGID=<GID> \
        -v <path/to/animes>:/animes \
        -v <path/to/movies>:/movies \
        -v <path/to/tvseries>:/tv \
        -e DOPPLERR_LANGUAGES="fra,eng" \
        stibbons31/dopplerr

Mount your media directories in `/`. Typically, `/animes` and `/tv` are from Sonarr, and
`/movies` from Radarr. A `/media` directory also exists in the docker image, so you can mount
them all in `/media` and set the following environment variable: `DOPPLERR_BASEDIR=/media`.

It is a good practice to run Sonarr and Radarr in their own container, so they also "see" their
media in path such as `/series`, `/tv`, `/animes`. Mount these volume with the same name in the
`dopplerr` container. `DOPPLERR_MAPPING` allows developers to run dopplerr directly from their
PC and allow a different naming conventions (for instance, `/path/to/Movies` is where the
movies are stored, but in all containers see it mounted as `/movies`).

#### Parameters

The parameters are split into two halves, separated by a colon, the left hand side representing the host and the right the container side. For example with a port -p external:internal - what this shows is the port mapping from internal to external of the container. So, `-p 8080:80` would expose port 80 from inside the container to be accessible from the host's IP on port 8080 (Ex: `http://192.168.x.x:8080`).

Example of starting command line arguments:

-   `-p 8086:8086` - the port webinterface
-   `-v /path/to/anime:/anime` - location of Anime library on disk
-   `-v /path/to/movies:/movies` - location of Movies library on disk
-   `-v /path/to/tv:/tv` - location of TV library on disk
-   `-e PGID=1000` - for GroupID. See below for explanation
-   `-e PUID=100` - for UserID. See below for explanation
-   `-e DOPPLERR_LANGUAGES=fra,eng` - set wanted subtitles languages (mandatory)
-   `-e DOPPLERR_VERBOSE=1` - set verbosity. 1=verbose, 0=silent (optional)

Developers might also use:

-   `-e DOPPLERR_BASEDIR=/media` - set media base directory (optional)
    (needs something like `-v /path/to/anime:/media/anime` and so on)

#### User / Group Identifiers

Sometimes when using data volumes (-v flags) permissions issues can arise between the host OS and the container. We avoid this issue by allowing you to specify the user PUID and group PGID. Ensure the data volume directory on the host is owned by the same user you specify and it will "just work" (TM).

In this instance PUID=1001 and PGID=1001. To find yours use id user as below:

    $ id <dockeruser>
    uid=1001(dockeruser) gid=1001(dockergroup) groups=1001(dockergroup)

#### Wanted subtitle languages

Use a comma-separated list of 3-letter language descriptors you want Subliminal to try to download them.

Example:

    DOPPLERR_LANGUAGES=fra,eng

Descriptors are ISO-639-3 names of the language. See the [official Babelfish table](https://github.com/Diaoul/babelfish/blob/f403000dd63092cfaaae80be9f309fd85c7f20c9/babelfish/data/iso-639-3.tab) to find your prefered languages.

### Local installation:

Create a dedicated virtual environment and install it properly with the following commands:

    $ sudo ./bootstrap-system.sh
    $ make install-local

This will install dopplerr in a local virtual environment will all its dependencies without messing with your system's Python environment.

### Installing in your system

Do NOT install a Python application in your system. Always use a Virtualenv. Or let it be handled by your distribution's maintainer.

This method is used when building the docker image (and the travis build):

    $ sudo ./bootstrap-system.sh
    $ sudo make install-system

### Radarr/Sonarr Configuration

Go in Settings to configure a "Connect" WebHook:

-   Settings &gt; Connect &gt; add WebHook notification
-   Select **On Download** and **On Upgrade**
-   URL: ```http://<ip address>:8086/api/v1/notify/sonarr```

    or

    URL: ```http://<ip address>:8086/api/v1/notify/radarr```
-   Method: POST

Two READMEs ?
-------------

There is a little trick to know about READMEs:

-   Docker Hub does not render README written in restructuredText correctly
-   Pypi does not render README written in Markdown correctly

So, a restructuredText version of the README is created from `README.md` on upload to Pypi.
Simple. So, when updating `README.md`, do not forget to regenerate `README.rst` using `make readme`.

Contributing
------------

Bootstrap your system with

    $ sudo ./bootstrap-system.sh

System dependencies:

- `git`
- `make`
- `pandoc`
- `pip`
- `pipenv`

Setup your environment with

    $ make dev

Unit Tests with:

    $ make test-unit

or run it live with

    $ make run-local

Activate the environment (to start your editor from, for example):

    $ make shell

Publishing to Pypi
------------------

(This part should be automatically done by Travis on successful tag build)

Build Wheel package:

    $ make wheels

Register and publish your package to Pypi:

    $ make pypi-publish

Create a release: create a tag with a Semver syntax. Optionally you can tag code locally and push to GitHub.

    $ git tag 1.2.3
    $ git push --tags

On successful travis build on the Tag branch, your Pypi package will be automatically updated.
