#!/bin/bash

OS=$(uname)
DOCKER_VERSION=$(docker -v | cut -d ' ' -f3 | cut -d ',' -f1)

docker-compose -f docker-compose.prod.yml exec web python user_manip.py $@
