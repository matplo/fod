#!/bin/bash

[ -z ${FOD_DIR} ] && echo "FOD_DIR not set" && exit 1
cd ${FOD_DIR}
source ${FOD_DIR}/scripts/util.sh
separator "${BASH_SOURCE}"

echo_info "Executing command: $@"
docker-compose -f docker-compose.prod.yml exec --user root web $@
