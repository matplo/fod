#!/bin/sh

# Ensure required runtime directories exist and have proper permissions
mkdir -p /home/app/web/project/static/proc_out /home/app/web/project/media
if [ "$(id -u)" = "0" ]; then
    chown -R app:app /home/app
    chmod -R u+rwX /home/app/web/project/static /home/app/web/project/media
fi

if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $SQL_HOST $SQL_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

if [ "$(id -u)" = "0" ]; then
    export HOME=/home/app
    exec gosu app "$@"
else
    exec "$@"
fi

