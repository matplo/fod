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
