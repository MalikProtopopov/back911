#!/bin/bash

# обновление сертификатов
docker-compose -f docker-compose.preprod.yml run --rm certbot renew

docker-compose -f docker-compose.preprod.yml exec nginx_test nginx -s reload