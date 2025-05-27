#!/bin/bash

docker_error() {
  echo -e "Docker command failed: unable to access Docker."
  echo -e "Please make sure docker is installed and you have the necessary permissions!"
  echo -e "Exiting!"
  exit
} 

python_error() {
  echo -e "Please make sure python3 is installed!\nExiting!"
  exit
}

pip_error() {
  echo -e "Please make sure pip is installed!\nExiting!"
  exit
}

virtualenv_error() {
  echo -e "Please make sure virtualenv is installed!\nExiting!"
  exit
}

pre_check() {
  docker ps > /dev/null 2>&1 || docker_error
  python3 -V > /dev/null 2>&1 || python_error
  pip -V > /dev/null 2>&1 || pip_error
  virtualenv --version > /dev/null 2>&1 || virtualenv_error
}

pre_check

echo -e "Pulling latest docker image...\n"
docker image pull itzg/minecraft-server > /dev/null 2>&1 || docker_error

virtualenv env >/dev/null
source env/bin/activate

echo -e "Installing all requirements...\n"
pip install -r requirements.txt > /dev/null

echo -e "Everything was set up successfully!"