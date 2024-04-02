if [ "$1" == "dev" ]; then
	if [ "$2" == "build" ]; then
		docker-compose down -v
		docker-compose up -d --build
	else
		docker-compose down
		docker-compose up -d
	fi
elif [ "$1" == "prod" ]; then
	if [ "$2" == "build" ]; then
		docker-compose -f docker-compose.prod.yml down -v
		docker-compose -f docker-compose.prod.yml up -d --build
		./make_db_prod.sh
	else
		docker-compose -f docker-compose.prod.yml down
		docker-compose -f docker-compose.prod.yml up -d
		./make_db_prod.sh
	fi
else
	echo "Invalid argument. Please use 'dev' or 'prod'."
fi
