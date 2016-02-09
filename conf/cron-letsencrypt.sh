# Django DBBackup script to run via cron
# Copyright (c) 2015 PushingKarma. All rights reserved.
# @monthly /home/mjs7231/Projects/pushingkarma/conf/cron-letsencrypt.sh >> /home/mjs7231/Logs/pushingkarma/cron-letsencrypt.log 2>&1
export DOMAINS='-d pushingkarma.com'
export DIR='/tmp/letsencrypt-auto'
mkdir -p $DIR
/home/mjs7231/Sources/letsencrypt/letsencrypt-auto certonly --renew -a webroot --webroot-path=$DIR $DOMAINS
service nginx reload
