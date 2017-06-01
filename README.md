# Subtitle Downloader Service

[![Build Status](https://travis-ci.org/Stibbons/subdlsrv.svg?branch=master)](https://travis-ci.org/Stibbons/subdlsrv)
[![Pyup](https://pyup.io/repos/github/Stibbons/subdlsrv/shield.svg)](https://pyup.io/repos/github/Stibbons/subdlsrv/)
[![Coveralls](https://coveralls.io/repos/github/Stibbons/subdlsrv/badge.svg)](https://coveralls.io/github/Stibbons/subdlsrv)
[![Pypi package](https://badge.fury.io/py/subdlsrv.svg)](https://pypi.python.org/pypi/subdlsrv/)
[![MIT licensed](https://img.shields.io/badge/license-MIT-blue.svg)](./LICENSE)

Subtitle Download Web Service for Sonarr or Radarr

* Free software: MIT
* Source: https://github.com/Stibbons/subdlsrv
* Python 3. Python 2 is tested by Travis but local installation is not provided.


## Usage

The best usage is through the docker image.

### Use with Docker

Use my docker image:

```
docker pull stibbons31/subdlsrv
```

Mount your media directory in `/media`. This directory exists in the docker image, so if you have
several media directory (`/series`, `/tv`, `/animes`), mount them all in `/media` and set the
following environment variable: `SUBDLSRC_BASE=/media`.

It is a good practive to run Sonarr and Radarr in their own container, so they also "see" their
media in `/series`, `/tv`, `/animes`. They will communicate these path to subdlsrv. Base directory
(`SUBDLSRC_BASE`) can be used to put all these folder in same directory. If `SUBDLSRC_BASE` is not
defined, subdlsrv will assume the path communicated by Sonarr or Radarr also exists locally. So
mouth your series folder to `/series`, TV show folder to `/tv`, and animes to `/animes` and so  on.

### Local installation:

Create a dedicated virtual environment and install it properly with the following commands:

```
sudo ./bootstrap.sh
./install.sh prod
```

This will install subdlsrv in a local virtual environment will all its dependencies without messing
with your system's Python environment.

### Installing in your system

Do NOT install a Python application in your system. Use Virtualenv. Or let it do by your
distribution's maintainer.

## Contributing

Bootstrap your system with
```
sudo ./bootstrap.sh
```

Setup your environment with
```
./install.sh
```

Test with:
```
./test-local.sh
```

or run it live with
```
./dev.sh
```

Activate the environment (to start your editor from, for example):

```
$ pipenv shell
```

## Publishing

(This part should be automatically done by Travis)

Build Wheel package:

```
pipenv run python setup.py bdist_wheel
```

Register and publish your package to Pypi:

```
pipenv run python setup.py sdist register upload
```

Create a release: create a tag with a semver syntax. Optionally you can tag code locally and push
to GitHub.

```
git tag 1.2.3
```

On successful travis build on the Tag branch, your Pypi package will be automatically updated.
