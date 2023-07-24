#!/usr/bin/env bash

echo "i am $(whoami)"

cd /vagrant/
source $HOME/venv_hanabira/bin/activate
python ./serve.py confs/development.ini >> /vagrant/service.log
