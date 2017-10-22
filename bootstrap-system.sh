#!/bin/bash

echo "Bootstrap system dependencies"
echo "sudo it accodingly to your system"
# git              : For PBR
# make             : Developer's toolbox
# pandoc           : for README .md =>.rst
# npm              : for building frontend
# libpython3.6-dev : for 'Python.h' (if Twisted wheel rebuild is needed)

if [ -f /etc/debian_version ]; then
    apt-get -y install \
               git \
               make \
               pandoc \
               libpython3.6-dev \
               nodejs
elif [ -f /etc/redhat-release ]; then
    yum install git make pandoc
elif [[ -f /etc/os-release && $(grep "alpine" /etc/os-release) != "" ]]; then
    echo "Alpine dependencies should be described in Dockerfile"
# elif [ -f /etc/??? ]; then
#     brew install pip pipenv make git pandoc
else
    echo "Please ensure 'git', 'make', and 'pandoc' and 'Python.h' headers are installed on your system"
fi
echo "Done"
