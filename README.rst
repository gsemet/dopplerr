Subtitle Downloader Service
===========================

|Build Status| |Docker Automated buil| |Pyup| |Coveralls| |Pypi package|
|PyPI| |MIT licensed|

.. |Build Status| image:: https://travis-ci.org/Stibbons/subdlsrv.svg?branch=master
   :target: https://travis-ci.org/Stibbons/subdlsrv
.. |Docker Automated buil| image:: https://img.shields.io/docker/build/stibbons31/subdlsrv.svg
   :target: https://hub.docker.com/r/stibbons31/subdlsrv/builds/
.. |Pyup| image:: https://pyup.io/repos/github/Stibbons/subdlsrv/shield.svg
   :target: https://pyup.io/repos/github/Stibbons/subdlsrv/
.. |Coveralls| image:: https://coveralls.io/repos/github/Stibbons/subdlsrv/badge.svg
   :target: https://coveralls.io/github/Stibbons/subdlsrv
.. |Pypi package| image:: https://badge.fury.io/py/subdlsrv.svg
   :target: https://pypi.python.org/pypi/subdlsrv/
.. |PyPI| image:: https://img.shields.io/pypi/stibbons/subdlsrv.svg
   :target: https://pypi.python.org/pypi/subdlsrv/
.. |MIT licensed| image:: https://img.shields.io/badge/license-MIT-blue.svg
   :target: ./LICENSE

Subtitle Download Web Service for Sonarr or Radarr. It can automatically
search for subtitles when the file has been successfully downloaded.

-  Free software: MIT
-  Source: https://github.com/Stibbons/subdlsrv
-  Python 3. Python 2 is tested by Travis but local installation is not
   provided.

Usage
-----

The best usage is through the docker image.

Use with Docker
~~~~~~~~~~~~~~~

Use my docker image:

::

    docker create \
        --name subdlsrv \
        -p 8000:8000 \
        -e PUID=<UID> \
        -e PGID=<GID> \
        -v <path/to/animes>:/animes \
        -v <path/to/movies>:/movies \
        -v <path/to/tvseries>:/tv \
        stibbons31/subdlsrv

Mount your media directory in ``/media``. This directory exists in the
docker image, so if you have several media directory (``/series``,
``/tv``, ``/animes``), mount them all in ``/media`` and set the
following environment variable: ``SUBDLSRC_BASEDIR=/media``.

It is a good practive to run Sonarr and Radarr in their own container,
so they also "see" their media in path such as ``/series``, ``/tv``,
``/animes``. Mount these volume with the same name in the subdlsrv
container. They will all communicate with the same path.

Base directory (``SUBDLSRC_BASEDIR environment variable``) can be used
to put all these folder in same directory. If ``SUBDLSRC_BASEDIR`` is
not defined, subdlsrv will assume the path communicated by Sonarr or
Radarr also exists locally. So mouth your series folder to ``/series``,
TV show folder to ``/tv``, and animes to ``/animes`` and so on.

Parameters
^^^^^^^^^^

The parameters are split into two halves, separated by a colon, the left
hand side representing the host and the right the container side. For
example with a port -p external:internal - what this shows is the port
mapping from internal to external of the container. So -p 8080:80 would
expose port 80 from inside the container to be accessible from the
host's IP on port 8080 http://192.168.x.x:8080 would show you what's
running INSIDE the container on port 80.

-  ``-p 8000`` - the port webinterface
-  ``-v /anime`` - location of Anime library on disk
-  ``-v /movies`` - location of Movies library on disk
-  ``-v /tv`` - location of TV library on disk
-  ``-e PGID for for GroupID`` - see below for explanation
-  ``-e PUID for for UserID`` - see below for explanation
-  ``-e SUBDLSRC_LANGUAGES`` - set wanted subtitles languages
   (mandatory)
-  ``-e SUBDLSRC_BASEDIR`` - set media base directory (optional)
-  ``-e SUBDLSRC_VERBOSE`` - set verbosity. 1=verbose, 0=silent
   (optional)

User / Group Identifiers
^^^^^^^^^^^^^^^^^^^^^^^^

Sometimes when using data volumes (-v flags) permissions issues can
arise between the host OS and the container. We avoid this issue by
allowing you to specify the user PUID and group PGID. Ensure the data
volume directory on the host is owned by the same user you specify and
it will "just work" TM.

In this instance PUID=1001 and PGID=1001. To find yours use id user as
below:

::

    $ id <dockeruser>
    uid=1001(dockeruser) gid=1001(dockergroup) groups=1001(dockergroup)

Wanted subtitle languages
^^^^^^^^^^^^^^^^^^^^^^^^^

Use a comma-separated list of 3-letter language descriptors you want
Subliminal to try to download them.

Example:

::

    SUBDLSRC_LANGUAGES=fra,eng

Descriptors are ISO-639-3 names of the language. See the `official
Babelfish
table <https://github.com/Diaoul/babelfish/blob/f403000dd63092cfaaae80be9f309fd85c7f20c9/babelfish/data/iso-639-3.tab>`__
to find your prefered languages.

Local installation:
~~~~~~~~~~~~~~~~~~~

Create a dedicated virtual environment and install it properly with the
following commands:

::

    sudo ./bootstrap.sh
    ./install.sh prod

This will install subdlsrv in a local virtual environment will all its
dependencies without messing with your system's Python environment.

Installing in your system
~~~~~~~~~~~~~~~~~~~~~~~~~

Do NOT install a Python application in your system. Use Virtualenv. Or
let it do by your distribution's maintainer.

This method is used when building the docker image:

::

    sudo ./bootstrap.sh
    sudo ./install.sh system

Radarr/Sonarr Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Configure a webhook:

-  **On Download/On Upgrade**
-  URL: http://:8086/notify
-  Method: POST

Contributing
------------

Bootstrap your system with

::

    sudo ./bootstrap.sh

Setup your environment with

::

    ./install.sh

Test with:

::

    ./test-local.sh

or run it live with

::

    ./dev.sh

Activate the environment (to start your editor from, for example):

::

    $ pipenv shell

Publishing
----------

(This part should be automatically done by Travis)

Build Wheel package:

::

    pipenv run python setup.py bdist_wheel

Register and publish your package to Pypi:

::

    pipenv run python setup.py sdist bdist bdist_wheel upload -r pypi

Create a release: create a tag with a semver syntax. Optionally you can
tag code locally and push to GitHub.

::

    git tag 1.2.3

On successful travis build on the Tag branch, your Pypi package will be
automatically updated.
