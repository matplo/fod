#!/bin/bash

[ -z ${FOD_DIR} ] && echo "FOD_DIR not set" && exit 1
cd ${FOD_DIR}
source ${FOD_DIR}/scripts/util.sh
separator "${BASH_SOURCE}"

docker-compose -f docker-compose.prod.yml exec web python user_manip.py $@

if [[ $@ =~ "add" ]] || [[ $@ =~ "delete" ]] || [[ $@ =~ "update" ]]; then
	if [[ $@ =~ "-u" ]] || [[ $@ =~ "--username" ]]; then
		echo_warning "REcreating database"
		docker-compose -f docker-compose.prod.yml exec web python manage.py create_db
		docker-compose -f docker-compose.prod.yml exec web python manage.py seed_db
	fi
fi
