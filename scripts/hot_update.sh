#!/bin/bash

[ -z ${FOD_DIR} ] && echo "FOD_DIR not set" && exit 1
cd ${FOD_DIR}
source ${FOD_DIR}/scripts/util.sh
separator "${BASH_SOURCE}"

# Step 1: Update python scripts, media files, templates, and pages
# Assuming your updates are in a Git repository, you can pull the latest changes
git pull

container_id=$(docker ps -qf "name=web")
container_name=$(docker ps | grep ${container_id} | awk '{print $NF}')

docker ps
note_red "Using container ID: $container_id"
note_red "Using container Name: $container_name"

# Step 2: Copy the updated files to the Docker volumes
# Replace /path/to/your/files with the actual path to your files
docker cp services/web/project/static/. ${container_name}:/home/app/web/project/static
docker cp services/web/project/media/. ${container_name}:/home/app/web/project/media
docker cp services/web/project/pages/. ${container_name}:/home/app/web/project/pages
docker cp services/web/project/templates/. ${container_name}:/home/app/web/project/templates

if [ -d services/web/project/scripts/external ]; then
	docker cp services/web/project/scripts/external ${container_name}:/home/app/web/project/scripts
fi

# Find all .py files and copy them to the corresponding directories in the Docker container
find services/web -name '*.py' | while read file; do
    docker cp "$file" "${container_name}:/home/app/web/${file#services/web/}"
    # echo "$file" "->" "${container_name}:/home/app/web/${file#services/web/}"
done

# Find all .yaml files and copy them to the corresponding directories in the Docker container
find services/web -name '*.yaml' | while read file; do
    docker cp "$file" "${container_name}:/home/app/web/${file#services/web/}"
    # echo "$file" "->" "${container_name}:/home/app/web/${file#services/web/}"
done

${FOD_DIR}/fod.sh web_exec chown -R app:app /home/app/

# Step 3: Restart gunicorn or the whole web service
# This command restarts the web service
docker-compose -f docker-compose.prod.yml restart web
