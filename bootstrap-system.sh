#!/bin/bash

echo "Bootstrap system tools"
echo "sudo it accodingly to your system"

if [ -f /etc/debian_version ]; then
    apt-get install git make pandoc
elif [ -f /etc/redhat-release ]; then
    yum install git make
# elif [ -f /etc/??? ]; then
#     brew install pip pipenv make git pandoc
else
    echo "Please ensure 'git', 'make', and 'pandoc' are installed on your system"
fi

# Freeze the version of pip and pipenv for setup reproductibility
pip install -U 'pip==9.0' 'pipenv==4.1.4' 'setuptools!=36.0.0' || echo "you may need to sudo me !"
echo "Done"
