#!/bin/bash

[ -z ${FOD_DIR} ] && echo "FOD_DIR not set" && exit 1
cd ${FOD_DIR}
source ${FOD_DIR}/scripts/util.sh
separator "${BASH_SOURCE}"

echo_help_message()
{
	echo_warning "[i] usage: ${BASH_SOURCE[0]} dev|prod"
	echo_warning "    dev: start the development environment"
	echo_warning "    prod: start the production environment"
}

what=$1
if [ -z "$what" ]; then
	echo_warning "[i] No argument provided - assuming prod"
	echo_help_message
	what="prod"
	echo_help_message
fi

if [ "$what" == "dev" ]; then
	docker-compose down
	exit 0
elif [ "$what" == "prod" ]; then
	docker-compose -f docker-compose.prod.yml down
	exit 0
else
	echo_help_message
	exit 1
fi
