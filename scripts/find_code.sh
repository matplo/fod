#!/bin/bash

#!/bin/bash

[ -z ${FOD_DIR} ] && echo "FOD_DIR not set" && exit 1
cd ${FOD_DIR}
source ${FOD_DIR}/scripts/util.sh
separator "${BASH_SOURCE}"

function usage() {
	echo_warning "Usage: $0 <string> [in_dir]"
	echo_warning "Find all files in in_dir (default: ${PWD} that contain the string"
	exit 0
}
if [ "$1" == "help" ]; then
	usage
fi

in_dir=$2
if [ -z $2 ]; then
		in_dir=${PWD}
fi

pattern=$3
if [ -z $3 ]; then
		pattern="*.*"
fi

string_to_find=$1
if [ -z ${string_to_find} ]; then
	echo_error "[e] String to find not provided"
	usage
fi

echo_warning "Searching for ${string_to_find} in ${in_dir} with pattern ${pattern}"
find ${in_dir} -name "${pattern}" -exec grep -H ${string_to_find} {} \;
