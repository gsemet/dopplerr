#!/bin/bash

echo "Bootstrap system tools"
echo "sudo it accodingly to your system"

# Freeze the version of pip and pipenv for setup reproductibility
pip install -U pip==9.0.1 pipenv==4.1.2 'setuptools<36' || echo "you may need to sudo me !"
echo "Done"
