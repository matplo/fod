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

## SSL/TLS Certificates & Automatic Renewal

FOD uses Let's Encrypt certificates managed via Dockerized Certbot and Nginx with **zero downtime**. Port 80 automatically answers ACME HTTP-01 challenges under `/.well-known/acme-challenge/` and redirects all regular web traffic to HTTPS.

### 1. Renew On-Demand (Single Command)

On your deployment server, run:

```bash
fod renew_cert <yourdomain.com> <youremail@example.com>
```

Example:
```bash
fod renew_cert ploskon.org admin@ploskon.org
```

Or define `DOMAIN` and `CERT_EMAIL` in `.env.prod`:
```bash
DOMAIN=ploskon.org
CERT_EMAIL=admin@ploskon.org
```
Then simply run:
```bash
fod renew_cert
```

This command:
1. Runs an ephemeral `certbot/certbot` Docker container to solve the HTTP challenge via Nginx (`/var/www/certbot`).
2. Copies `fullchain.pem` and `privkey.pem` into `./certificates/` with secure permissions.
3. Gracefully reloads Nginx (`nginx -s reload`) with **zero downtime** and no container restarts.

To force immediate renewal:
```bash
fod renew_cert --force
```

### 2. Fully Automated Renewal (Cron)

Add a monthly cron job on your deployment host to automatically renew certificates before they expire:

```bash
crontab -e
```

Add the following entry (runs at 03:00 on the 1st of every month):
```cron
0 3 1 * * /path/to/fod/scripts/fod.sh renew_cert >> /var/log/fod_cert_renew.log 2>&1
```
Certbot will check certificate expiration and only renew when within 30 days of expiry.

