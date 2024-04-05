#!/bin/bash

function thisdir()
{
	SOURCE="${BASH_SOURCE[0]}"
	while [ -h "$SOURCE" ]; do # resolve $SOURCE until the file is no longer a symlink
		DIR="$( cd -P "$( dirname "$SOURCE" )" >/dev/null 2>&1 && pwd )"
		SOURCE="$(readlink "$SOURCE")"
		[[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE" # if $SOURCE was a relative symlink, we need to resolve it relative to the path where the symlink file was located
	done
	DIR="$( cd -P "$( dirname "$SOURCE" )" >/dev/null 2>&1 && pwd )"
	echo ${DIR}
}
THISD=$(thisdir)
export FOD_DIR=${THISD}

source ${THISD}/scripts/util.sh
separator "fod: ${BASH_SOURCE}"


help=$(get_opt "help" $@)
opt=$1
if [ ! -z ${help} ] || [ -z ${opt} ]; then
	echo "[i] usage: ${BASH_SOURCE[0]} [--help] command"
	echo "    --help: print this help message"
	cmnds=$(ls ${FOD_DIR}/scripts | grep -v util.sh | sed 's/\.sh//g' | tr '\n' ' ' | sort)
	echo "    command: the command to run - any from ${cmnds}"
	exit 0
fi

cd ${FOD_DIR}
separator "fod: ${@}"

cmd=$(echo $opt | sed 's/--//g')
if [ -f ${FOD_DIR}/scripts/${cmd}.sh ]; then
	shift
	separator "${FOD_DIR}/scripts/${cmd}.sh"
	${FOD_DIR}/scripts/${cmd}.sh $@
else
	echo "[e] command not found: ${cmd}"
	exit 1
fi
separator "fod: ${BASH_SOURCE} done"