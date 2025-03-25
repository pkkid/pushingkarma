#!/usr/bin/env python
# Database Backup
# Saves a backup of the current database to Synology
import shutil, sys
import logging as log
from datetime import datetime
from os.path import dirname, abspath

logformat = '%(asctime)-.19s %(module)16s:%(lineno)-3s %(levelname)-7s %(message)s'
log.basicConfig(stream=sys.stdout, level=log.INFO, format=logformat)

ROOT = dirname(dirname(abspath(__file__)))
LOCAL_SOURCE = f'{ROOT}/pk/db.sqlite3'
REMOTE_DEST = '/volume1/Synology/Michael/Backup/PushingKarma/pushingkarma-{dtstr}.sqlite3'
_ = lambda path: path.replace(ROOT, '')


if __name__ == '__main__':
    dtstr = datetime.now().strftime('%Y-%m-%d')
    remote_dest = REMOTE_DEST.replace('{dtstr}', dtstr)
    log.info(f'Saving {_(LOCAL_SOURCE)} to {remote_dest}')
    shutil.copy(LOCAL_SOURCE, remote_dest)
