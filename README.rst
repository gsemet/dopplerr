===========================
Subtitle Downloader Service
===========================

.. image:: https://travis-ci.org/Stibbons/subdlsrv.svg?branch=master
    :target: https://travis-ci.org/Stibbons/subdlsrv
.. image:: https://pyup.io/repos/github/Stibbons/subdlsrv/shield.svg
     :target: https://pyup.io/repos/github/Stibbons/subdlsrv/
     :alt: Updates
.. image:: https://coveralls.io/repos/github/Stibbons/subdlsrv/badge.svg
   :target: https://coveralls.io/github/Stibbons/subdlsrv
.. image:: https://badge.fury.io/py/subdlsrv.svg
   :target: https://pypi.python.org/pypi/subdlsrv/
   :alt: Pypi package
.. image:: https://img.shields.io/badge/license-MIT-blue.svg
   :target: ./LICENSE
   :alt: MIT licensed

Subtitle Download Web Service for Sonarr or Radarr

* Free software: MIT
* Source: https://github.com/Stibbons/subdlsrv
* Python 3. Python 2 is tested by Travis but local installation is not provided.


Usage
-----

The best usage is through the docker image. Use:

    docker pull stibbons31/subdlsrv

Mount your media directory in `/media`. This directory exists in the docker image, so if you have
several media directory (`/series`, `/tv`, `/animes`), mount them all in `/media` and set the
following environment variable: `SUBDLSRC_BASE=/media`.

It is a good practive to run Sonarr and Radarr in their own container, so they also "see" their
media in `/series`, `/tv`, `/animes`. They will communicate these path to subdlsrv. Base directory
(`SUBDLSRC_BASE`) can be used to put all these folder in same directory. If `SUBDLSRC_BASE` is not
defined, subdlsrv will assume the path communicated by Sonarr or Radarr also exists locally. So
mouth your series folder to `/series`, TV show folder to `/tv`, and animes to `/animes` and so  on.

To use locally, execute:

    sudo ./bootstrap.sh
    ./install.sh prod

This will install subdlsrv in a local virtual environment will all its dependencies without messing
with your system's Python environment.

Contributing
------------

Bootstrap your system with

    sudo ./bootstrap.sh

Setup your environment with

    ./install.sh

Test with:

    ./test-local.sh

or run it live with

    ./dev.sh

Activate the environment (to start your editor from, for example):

    .. code-block:: bash

        $ pipenv shell

Publishing
----------

(This part should be automatically done by Travis)

Build Wheel package:

.. code-block:: bash

    pipenv run python setup.py bdist_wheel


Register and publish your package to Pypi:

.. code-block:: bash

    pipenv run python setup.py sdist register upload

Create a release: create a tag with a semver syntax. Optionally you can tag code locally and push
to GitHub.

.. code-block:: bash

    git tag 1.2.3

On successful travis build on the Tag branch, your Pypi package will be automatically updated.
