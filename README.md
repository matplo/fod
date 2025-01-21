# Dockerizing Flask with Postgres, Gunicorn, and Nginx

- built on top of https://github.com/testdrivenio/flask-on-docker
- added some extra features (https only, redis, dynamic execution of scripts based on template.meta data etc)
- note: only "Production" functional

## Startup

- make sure to put your certificates in `./certificates`

```
-rw-r--r--  cert.pem
-rw-------  privkey.pem
```

- then

```
. ./init.sh
prod.sh up prod build
```

- visit: https://localhost

- hint: use tab after typing `prod.sh` - some predefined util scripts/commands available
    - for example: `prod.sh hot_update` puts things into web image and restarts it - updates available pronto

## Renew certificates - quick

### enable port 80 in the nginx

- edit the nginx configuration in .yml

```
nginx:
  build: ./services/nginx
  volumes:
    - ./certificates:/etc/nginx/ssl
    - static_volume:/home/app/web/project/static
    - media_volume:/home/app/web/project/media
    - pages_volume:/home/app/web/project/pages
    - templates_volume:/home/app/web/project/templates
  ports:
    - 80:80  # Added to enable HTTP challenge
    - 443:443
  depends_on:
    - web
```

### restart

- `fod restart`

### run certbot (host)

- then in the host (not within docker):

```
sudo certbot certonly --standalone -d yourdomain.com
```

- note, you may need to install certbot
```
sudo apt update
sudo apt install certbot python3-certbot-nginx
```

### copy the new certificates
- copy the certs where they belong (from `/etc/letsencrypt/live` in your host; note will need root priv; remember chown then...)

```
cp /etc/letsencrypt/live/<yourdomain.com>/cert.pem <wherefod>/fod/certificates/
cp /etc/letsencrypt/live/<yourdomain.com>/privkey.pem <wherefod>/fod/certificates/
```

### disable the port 80

- disable the 80:80 in the .yml file

## restart

- `fod restart`

