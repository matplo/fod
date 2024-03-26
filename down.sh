if [ "$1" == "dev" ]; then
	docker-compose down
	exit 0
elif [ "$1" == "prod" ]; then
	docker-compose -f docker-compose.prod.yml down
	exit 0
else
	echo "Invalid argument. Please use 'dev' or 'prod'."
	exit 1
fi
