#!/bin/bash

[ -z ${FOD_DIR} ] && echo "FOD_DIR not set" && exit 1
cd ${FOD_DIR}
source ${FOD_DIR}/scripts/util.sh
separator "${BASH_SOURCE}"

# Step 1: Update python scripts, media files, templates, and pages
# Assuming your updates are in a Git repository, you can pull the latest changes
git pull

docker ps
container_id=$(docker ps -qf "name=web")
if [ -z ${container_id} ]; then
    note_red "Web container not found. Exiting..."
    exit 1
fi
container_name=$(docker ps | grep ${container_id} | awk '{print $NF}')

note_red "Using container ID: $container_id"
note_red "Using container Name: $container_name"

# Step 2: Copy the updated files to the Docker volumes
for s in scripts pages templates views static media forms models
do
    echo_warning "Copying ${s} to ${container_name}:/home/app/web/project/"
	docker cp services/web/project/${s} ${container_name}:/home/app/web/project/
done

# # Find all .py files and copy them to the corresponding directories in the Docker container
# find services/web -name '*.py' | while read file; do
#     docker cp "$file" "${container_name}:/home/app/web/${file#services/web/}"
#     # echo "$file" "->" "${container_name}:/home/app/web/${file#services/web/}"
# done
# 
# # Find all .yaml files and copy them to the corresponding directories in the Docker container
# find services/web -name '*.yaml' | while read file; do
#     docker cp "$file" "${container_name}:/home/app/web/${file#services/web/}"
#     # echo "$file" "->" "${container_name}:/home/app/web/${file#services/web/}"
# done

${FOD_DIR}/fod.sh web_exec rm app.log
${FOD_DIR}/fod.sh web_exec chown -R app:app /home/app/

# Step 3: Restart gunicorn or the whole web service
# This command restarts the web service
docker-compose -f docker-compose.prod.yml restart web
