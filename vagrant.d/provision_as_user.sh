#!/usr/bin/env bash

DBNAME=hanadb
DBUSER=hana
DBPASSWD=some_password

echo -e "\n--- Configure hanabira environment ---\n"
cd /vagrant/
virtualenv --no-site-packages -p /usr/bin/python3 $HOME/venv_hanabira
echo "source $HOME/venv_hanabira/bin/activate" >> .profile
source $HOME/venv_hanabira/bin/activate
./requirements.sh

cp confs/development.ini.template confs/development.ini
sed -i "/sqlalchemy\.url.*/c\\sqlalchemy\.url = mysql+pymysql:\/\/${DBUSER}:${DBPASSWD}@127.0.0.1\/${DBNAME}\?charset=utf8" confs/development.ini

echo -e "\n--- Restart service ---\n"
sudo systemctl restart hana.service
sudo systemctl status hana.service
