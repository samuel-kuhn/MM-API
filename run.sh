#!/bin/bash
docker_error() {
  echo -e "Docker is not running or accessible!\nExiting!"
  exit 1
}

echo -e "pulling latest docker image...\n"
docker image pull itzg/minecraft-server > /dev/null 2>&1 || docker_error

source env/bin/activate

gunicorn --config gunicorn-cfg.py app:app
