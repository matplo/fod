docker logs flask-on-docker-web-1
echo "-------"
docker logs flask-on-docker-nginx-1

docker exec -it flask-on-docker-nginx-1 /bin/cat /var/log/nginx/access.log

