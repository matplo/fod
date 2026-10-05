#!/bin/bash

[ -z "${FOD_DIR}" ] && echo "FOD_DIR not set" && exit 1
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
mkdir -p "${WWW_DIR}" "${CONF_DIR}"

# Ensure Nginx is running to serve the ACME challenge
echo_info "[i] Verifying Nginx is running..."
if ! docker compose -f docker-compose.prod.yml ps nginx | grep -q "Up"; then
    echo_warning "[w] Nginx is not running. Starting Nginx..."
    docker compose -f docker-compose.prod.yml up -d nginx
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

CERT_SRC="${CONF_DIR}/live/${DOMAIN}"
CERT_DEST="${FOD_DIR}/certificates"

if [ -f "${CERT_SRC}/fullchain.pem" ] && [ -f "${CERT_SRC}/privkey.pem" ]; then
    echo_info "[i] Copying renewed certificates to ${CERT_DEST}/..."
    cp -L "${CERT_SRC}/fullchain.pem" "${CERT_DEST}/fullchain.pem"
    cp -L "${CERT_SRC}/fullchain.pem" "${CERT_DEST}/cert.pem"
    cp -L "${CERT_SRC}/privkey.pem"   "${CERT_DEST}/privkey.pem"
    if [ -f "${CERT_SRC}/chain.pem" ]; then
        cp -L "${CERT_SRC}/chain.pem" "${CERT_DEST}/chain.pem"
    fi

    chmod 644 "${CERT_DEST}/fullchain.pem" "${CERT_DEST}/cert.pem"
    chmod 600 "${CERT_DEST}/privkey.pem"

    echo_info "[i] Reloading Nginx configuration gracefully (zero downtime)..."
    docker compose -f docker-compose.prod.yml exec -T nginx nginx -s reload 2>/dev/null || \
    docker-compose -f docker-compose.prod.yml exec -T nginx nginx -s reload 2>/dev/null || \
    echo_warning "[w] Could not reload Nginx automatically. Run: fod restart"

    echo_info "[i] Certificate renewal complete!"
    if command -v openssl >/dev/null 2>&1; then
        echo_info "[i] Certificate validity:"
        openssl x509 -in "${CERT_DEST}/cert.pem" -noout -subject -dates
    fi
else
    echo_error "[e] Certificate files not found in ${CERT_SRC}"
    exit 1
fi

separator "fod: renew_cert done"
