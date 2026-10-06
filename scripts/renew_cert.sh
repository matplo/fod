#!/bin/bash

FOD_DIR="${FOD_DIR:-$(cd "$(dirname "$0")/.." && pwd)}"
cd "${FOD_DIR}"
source "${FOD_DIR}/scripts/util.sh"
separator "fod: renew_cert"

# Help message
if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    echo "Usage: fod renew_cert [DOMAIN] [EMAIL] [--force]"
    echo ""
    echo "Automatically renews or obtains Let's Encrypt SSL/TLS certificates using"
    echo "Dockerized Certbot (ACME HTTP-01 webroot challenge) with zero downtime."
    echo ""
    echo "Arguments:"
    echo "  DOMAIN    The domain name (e.g., ploskon.org). Defaults to DOMAIN in .env.prod"
    echo "  EMAIL     Contact email for Let's Encrypt. Defaults to CERT_EMAIL in .env.prod"
    echo "  --force   Force certificate renewal even if not expiring soon"
    echo ""
    echo "Automated Cron Example:"
    echo "  0 3 1 * * cd ${FOD_DIR} && ./scripts/fod.sh renew_cert >> /var/log/fod_cert_renew.log 2>&1"
    exit 0
fi

# Load variables from .env.prod if available
if [ -f "${FOD_DIR}/.env.prod" ]; then
    source <(grep -E '^(DOMAIN|SERVER_NAME|CERT_EMAIL)=' "${FOD_DIR}/.env.prod" 2>/dev/null)
fi

DOMAIN=""
EMAIL=""
FORCE_ARG=""

for arg in "$@"; do
    case "$arg" in
        --force)
            FORCE_ARG="--force-renewal"
            ;;
        *@*)
            EMAIL="$arg"
            ;;
        *)
            if [ -z "$DOMAIN" ]; then
                DOMAIN="$arg"
            fi
            ;;
    esac
done

# Fallbacks
DOMAIN="${DOMAIN:-${SERVER_NAME:-${DOMAIN}}}"
EMAIL="${EMAIL:-${CERT_EMAIL}}"

if [ -z "$DOMAIN" ]; then
    echo_error "[e] Domain not specified. Provide it as argument or set DOMAIN in .env.prod"
    echo "    Example: fod renew_cert ploskon.org admin@ploskon.org"
    exit 1
fi

echo_info "[i] Domain: ${DOMAIN}"
if [ -n "$EMAIL" ]; then
    echo_info "[i] Email:  ${EMAIL}"
    EMAIL_ARG="--email ${EMAIL} --no-eff-email"
else
    echo_warning "[w] No email provided. Proceeding with --register-unsafely-without-email"
    EMAIL_ARG="--register-unsafely-without-email"
fi

# Prepare webroot and cert storage directories
WWW_DIR="${FOD_DIR}/certificates/certbot/www"
CONF_DIR="${FOD_DIR}/certificates/certbot/conf"
CERT_DEST="${FOD_DIR}/certificates"

# Detect Docker Compose binary (docker compose vs docker-compose)
if docker compose version >/dev/null 2>&1; then
    COMPOSE_CMD="docker compose"
elif command -v docker-compose >/dev/null 2>&1; then
    COMPOSE_CMD="docker-compose"
else
    COMPOSE_CMD=""
fi

# Ensure directories exist (with Docker fallback in case host directory has root ownership)
if ! mkdir -p "${WWW_DIR}" "${CONF_DIR}" 2>/dev/null; then
    docker run --rm \
        --entrypoint sh \
        -v "${CERT_DEST}:/certificates:rw" \
        certbot/certbot -c "mkdir -p /certificates/certbot/www /certificates/certbot/conf && chmod -R a+rwx /certificates/certbot" 2>/dev/null || true
fi

# Ensure Nginx is running to serve the ACME challenge
echo_info "[i] Verifying Nginx is running..."
NGINX_RUNNING=0
if [ -n "$COMPOSE_CMD" ]; then
    if $COMPOSE_CMD -f docker-compose.prod.yml ps nginx 2>/dev/null | grep -qi "Up\|running"; then
        NGINX_RUNNING=1
    fi
fi
if [ "$NGINX_RUNNING" -eq 0 ] && docker ps --format '{{.Names}}' 2>/dev/null | grep -qi "nginx"; then
    NGINX_RUNNING=1
fi

if [ "$NGINX_RUNNING" -eq 0 ]; then
    echo_warning "[w] Nginx is not running. Starting Nginx..."
    if [ -n "$COMPOSE_CMD" ]; then
        $COMPOSE_CMD -f docker-compose.prod.yml up -d nginx
    fi
fi

echo_info "[i] Running Certbot in Docker (webroot ACME challenge)..."
docker run --rm \
    -v "${WWW_DIR}:/var/www/certbot:rw" \
    -v "${CONF_DIR}:/etc/letsencrypt:rw" \
    certbot/certbot certonly \
    --webroot \
    -w /var/www/certbot \
    -d "${DOMAIN}" \
    ${EMAIL_ARG} \
    --agree-tos \
    --non-interactive \
    ${FORCE_ARG} \
    --keep-until-expiring

echo_info "[i] Installing certificates into ${CERT_DEST}/..."
COPY_SUCCESS=0
if docker run --rm \
    --entrypoint sh \
    -v "${CONF_DIR}:/etc/letsencrypt:rw" \
    -v "${CERT_DEST}:/certificates:rw" \
    certbot/certbot -c "
        if [ -f /etc/letsencrypt/live/${DOMAIN}/fullchain.pem ] && [ -f /etc/letsencrypt/live/${DOMAIN}/privkey.pem ]; then
            cp -L /etc/letsencrypt/live/${DOMAIN}/fullchain.pem /certificates/fullchain.pem && \
            cp -L /etc/letsencrypt/live/${DOMAIN}/fullchain.pem /certificates/cert.pem && \
            cp -L /etc/letsencrypt/live/${DOMAIN}/privkey.pem /certificates/privkey.pem && \
            if [ -f /etc/letsencrypt/live/${DOMAIN}/chain.pem ]; then
                cp -L /etc/letsencrypt/live/${DOMAIN}/chain.pem /certificates/chain.pem
            fi && \
            chmod 644 /certificates/fullchain.pem /certificates/cert.pem && \
            chmod 600 /certificates/privkey.pem && \
            chmod -R a+rX /etc/letsencrypt 2>/dev/null || true
            exit 0
        else
            exit 1
        fi
    "; then
    COPY_SUCCESS=1
fi

if [ "$COPY_SUCCESS" -eq 1 ]; then
    echo_info "[i] Reloading Nginx configuration gracefully (zero downtime)..."
    RELOADED=0
    NGINX_CONTAINER=$(docker ps -qf "name=nginx" 2>/dev/null | head -n 1)
    if [ -n "$NGINX_CONTAINER" ]; then
        if docker exec "$NGINX_CONTAINER" nginx -s reload 2>/dev/null; then
            RELOADED=1
        fi
    fi
    if [ "$RELOADED" -eq 0 ] && [ -n "$COMPOSE_CMD" ]; then
        if $COMPOSE_CMD -f docker-compose.prod.yml exec -T nginx nginx -s reload 2>/dev/null; then
            RELOADED=1
        fi
    fi

    if [ "$RELOADED" -eq 1 ]; then
        echo_info "[i] Nginx reloaded successfully!"
    else
        echo_warning "[w] Could not reload Nginx automatically. Run: fod restart"
    fi

    echo_info "[i] Certificate renewal complete!"
    if command -v openssl >/dev/null 2>&1; then
        echo_info "[i] Certificate validity:"
        openssl x509 -in "${CERT_DEST}/cert.pem" -noout -subject -dates 2>/dev/null || true
    fi
else
    echo_error "[e] Certificate files for ${DOMAIN} were not found in ${CONF_DIR}/live/${DOMAIN}"
    exit 1
fi

separator "fod: renew_cert done"
