#!/bin/bash

[ -z ${FOD_DIR} ] && echo "FOD_DIR not set" && exit 1
cd ${FOD_DIR}
source ${FOD_DIR}/scripts/util.sh
separator "${BASH_SOURCE}"

TEST_DIR=${FOD_DIR}/test
mkdir -p ${TEST_DIR}
cd ${TEST_DIR}
if [ $1 == "clean" ]; then
	rm -rfv ./yasp ./requirements.txt
	exit 0
fi
if [ ! -d yasp ]; then
	git clone git@github.com:matplo/yasp.git
else
	cd yasp
	if [ "$1" == "update" ]; then
		git pull
	fi
	cd ..
fi

touch requirements.txt
sdiff=$(diff ${FOD_DIR}/services/web/requirements.txt requirements.txt)
if [ -z $sdiff ]; then
	echo_info "requirements.txt is up to date"
else
	echo_warning "requirements.txt is not up to date"
	cp ${FOD_DIR}/services/web/requirements.txt .
	${TEST_DIR}/yasp/yaspenv.sh pip install -r requirements.txt
fi
# cd ${FOD_DIR}/services/web/project
# export FLASK_APP=${FOD_DIR}/services/web/project.main.py
# ${TEST_DIR}/yasp/yaspenv.sh flask run
cd ${FOD_DIR}/services/web
${TEST_DIR}/yasp/yaspenv.sh python run.py
separator "${BASH_SOURCE} done"