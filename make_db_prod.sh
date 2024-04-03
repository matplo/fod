#!/bin/bash

user_manip() {
	docker-compose -f docker-compose.prod.yml exec web python user_manip.py $@
}
user_manip add --username test --password test --email test@test.com

docker-compose -f docker-compose.prod.yml exec web python manage.py create_db
docker-compose -f docker-compose.prod.yml exec web python manage.py seed_db

# this is to check if the db exists
docker-compose -f docker-compose.prod.yml exec db psql --username=hello_flask --dbname=hello_flask_prod -c "\l"
docker-compose -f docker-compose.prod.yml exec db psql --username=hello_flask --dbname=hello_flask_prod -c "\dt"
docker-compose -f docker-compose.prod.yml exec db psql --username=hello_flask --dbname=hello_flask_prod -c "SELECT * FROM users;"

# docker volume inspect flask-on-docker_postgres_data

user_manip list
