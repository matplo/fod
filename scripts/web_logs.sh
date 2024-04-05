#!/bin/bash

[ -z ${FOD_DIR} ] && echo "FOD_DIR not set" && exit 1
cd ${FOD_DIR}
source ${FOD_DIR}/scripts/util.sh
separator "${BASH_SOURCE}"

docker logs ${web_container_name}
docker logs ${nginx_container_name}

docker exec -it ${nginx_container_name} /bin/cat /var/log/nginx/access.log

