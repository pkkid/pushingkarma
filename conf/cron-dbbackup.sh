# Django DBBackup script to run via cron
# Copyright (c) 2015 PushingKarma. All rights reserved.
# @daily /home/mjs7231/Projects/pushingkarma/conf/dbbackup-cron.sh >> /home/mjs7231/Logs/pushingkarma/dbbackup.log 2>&1
cd /home/mjs7231/Projects/pushingkarma
export PYTHONPATH="/home/mjs7231/Projects/pushingkarma:$PYTHONPATH"
. /home/mjs7231/.virtualenvs/pushingkarma/bin/activate
. /home/mjs7231/.virtualenvs/pushingkarma/bin/postactivate
/home/mjs7231/.virtualenvs/pushingkarma/bin/python /home/mjs7231/Projects/pushingkarma/manage.py dbbackup --clean
