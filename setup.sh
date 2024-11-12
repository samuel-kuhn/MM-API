#!/bin/bash
if [ $USER != root ]
then
  echo -e "Please make sure you run this as root!\nExiting!"
  exit
fi

if ! command -v docker >/dev/null  2>&1
then
  echo -e "Please make sure docker is installed!\nExiting!"
  exit
fi
echo -e "pulling latest docker image...\n"
docker image pull itzg/minecraft-server > /dev/null

if ! command -v python3 >/dev/null  2>&1
then
  echo -e "Please make sure python3 is installed!\nExiting!"
  exit
fi

if ! command -v pip >/dev/null  2>&1
then
  echo -e "Please make sure pip is installed!\nExiting!"
  exit
fi

if ! command -v virtualenv >/dev/null  2>&1
then
  echo -e "installing virtualenv...\n"
  apt update >/dev/null && apt install python3-virtualenv -y >/dev/null  2>&1
fi
#enabling virtualenv
virtualenv env >/dev/null
source env/bin/activate

echo -e "installing all requirements...\n"
pip install -r requirements.txt > /dev/null

echo -e "Everything was set up successfully!"