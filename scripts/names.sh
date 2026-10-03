#!/bin/bash

[ -z ${FOD_DIR} ] && echo "FOD_DIR not set" && exit 1
cd ${FOD_DIR}
source ${FOD_DIR}/scripts/util.sh
separator "${BASH_SOURCE}"

load_container_info
echo_info "web_container_name   : ${web_container_name:-[not running]}"
echo_info "nginx_container_name : ${nginx_container_name:-[not running]}"
echo_info "redis_container_name : ${redis_container_name:-[not running]}"
echo_info "db_container_name    : ${db_container_name:-[not running]}"
