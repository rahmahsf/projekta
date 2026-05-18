#!/bin/bash

if ! [ -x "$(command -v docker-compose)" ]; then
  echo 'Error: docker-compose is not installed.' >&2
  exit 1
fi

domains=(rahmah.nasrulfahmi.my.id www.rahmah.nasrulfahmi.my.id)
rsa_key_size=4096
data_path="./certbot"
email="75nasrulfahmi@gmail.com" # Ganti dengan email aktif Anda
staging=0 # Set ke 1 jika Anda sedang tes agar tidak kena rate limit

if [ -d "$data_path" ]; then
  read -p "Data certbot lama sudah ada di $data_path. Teruskan dan timpa? (y/N) " decision
  if [ "$decision" != "Y" ] && [ "$decision" != "y" ]; then
    exit
  fi
fi


echo "### Mendownload TLS parameters ..."
mkdir -p "$data_path/conf"
curl -s https://raw.githubusercontent.com/certbot/certbot/master/certbot-nginx/certbot_nginx/_internal/tls_configs/options-ssl-nginx.conf > "$data_path/conf/options-ssl-nginx.conf"
curl -s https://raw.githubusercontent.com/certbot/certbot/master/certbot/certbot/ssl-dhparams.pem > "$data_path/conf/ssl-dhparams.pem"
echo

echo "### Membuat dummy certificate untuk $domains ..."
path="/etc/letsencrypt/live/$domains"
mkdir -p "$data_path/conf/live/$domains"
docker-compose -f docker-compose.prod.yml run --rm --entrypoint "\
  openssl req -x509 -nodes -newkey rsa:$rsa_key_size -days 1\
    -keyout '$path/privkey.pem' \
    -out '$path/fullchain.pem' \
    -subj '/CN=localhost'" certbot
echo


echo "### Menjalankan Nginx ..."
docker-compose -f docker-compose.prod.yml up --force-recreate -d nginx
echo

echo "### Menghapus dummy certificate ..."
docker-compose -f docker-compose.prod.yml run --rm --entrypoint "\
  rm -Rf /etc/letsencrypt/live/$domains && \
  rm -Rf /etc/letsencrypt/archive/$domains && \
  rm -Rf /etc/letsencrypt/renewal/$domains.conf" certbot
echo


echo "### Requesting Let's Encrypt certificate untuk $domains ..."
# Pilihan parameter
domain_args=""
for domain in "${domains[@]}"; do
  domain_args="$domain_args -d $domain"
done

# Pilih email argument
case "$email" in
  "") email_arg="--register-unsafely-without-email" ;;
  *) email_arg="--email $email" ;;
esac

# Tambah staging argument
if [ $staging != "0" ]; then staging_arg="--staging"; fi

docker-compose -f docker-compose.prod.yml run --rm --entrypoint "\
  certbot certonly --webroot -w /var/www/certbot \
    $staging_arg \
    $email_arg \
    $domain_args \
    --rsa-key-size $rsa_key_size \
    --agree-tos \
    --force-renewal" certbot
echo

echo "### Merestart Nginx ..."
docker-compose -f docker-compose.prod.yml exec nginx nginx -s reload
