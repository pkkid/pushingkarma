# Copyright (c) 2015 PushingKarma. All rights reserved.
cd /home/mjs7231/Projects/pushingkarma
export PYTHONPATH="/home/mjs7231/Projects/pushingkarma:$PYTHONPATH"
. /home/mjs7231/.virtualenvs/pushingkarma/bin/activate
. /home/mjs7231/.virtualenvs/pushingkarma/bin/postactivate
/home/mjs7231/.virtualenvs/pushingkarma/bin/python /home/mjs7231/Projects/pushingkarma/manage.py dbbackup --clean
