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

# Bash completion script
_fod_bash_completion() {
    local cur prev opts
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    # opts="--help --verbose --version"
		cmnds=$(ls ${FOD_DIR}/scripts | grep -v util.sh | sed 's/\.sh//g' | tr '\n' ' ' | sort)
    # if [[ ${cur} == -* ]] ; then
    if [[ ${cur} == * ]] ; then
        COMPREPLY=( $(compgen -W "${cmnds}" -- ${cur}) )
        return 0
    fi
}
complete -F _fod_bash_completion fod.sh
