#!/bin/bash

#!/usr/bin/env bash
set -euo pipefail

USER_OPT=""
if [[ "${1:-}" == "--root" || "${1:-}" == "-r" ]]; then
  USER_OPT="-u 0"
fi

# docker compose exec $USER_OPT web bash 2>/dev/null || docker compose exec $USER_OPT web sh

[ -z ${FOD_DIR} ] && echo "FOD_DIR not set" && exit 1
cd ${FOD_DIR}
source ${FOD_DIR}/scripts/util.sh
separator "${BASH_SOURCE}"

# docker-compose -f docker-compose.prod.yml exec web /bin/bash
# docker compose exec $USER_OPT web bash 2>/dev/null || docker compose exec $USER_OPT web sh
# docker-compose -f docker-compose.prod.yml $USER_OPT exec web /bin/bash 2>/dev/null || docker-compose -f docker-compose.prod.yml $USER_OPT exec web /bin/bash
echo "[i] running with user option: $USER_OPT"
docker-compose -f docker-compose.prod.yml exec $USER_OPT web /bin/bash
