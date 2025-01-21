#!/bin/bash

[ -z ${FOD_DIR} ] && echo "FOD_DIR not set" && exit 1
cd ${FOD_DIR}
source ${FOD_DIR}/scripts/util.sh
separator "${BASH_SOURCE}"

# docker exec -it fod_nginx /bin/bash
docker-compose -f docker-compose.prod.yml exec nginx /bin/bash
