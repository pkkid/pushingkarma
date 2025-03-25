#!/usr/bin/env python
# Database Backup
# Fetches the latest database backup from Synology
import os, subprocess, sys
import logging as log
from datetime import datetime
from os.path import abspath, dirname, exists

logformat = '%(asctime)-.19s %(module)16s:%(lineno)-3s %(levelname)-7s %(message)s'
log.basicConfig(stream=sys.stdout, level=log.INFO, format=logformat)

ROOT = dirname(dirname(abspath(__file__)))
REMOTE_SOURCE = 'synology:~/synology/Michael/Backup/PushingKarma/pushingkarma-{dtstr}.sqlite3'
LOCAL_TMP = f'{ROOT}/pk/db.sqlite3.tmp'
LOCAL_BAK = f'{ROOT}/pk/db.sqlite3.bak'
LOCAL_DEST = f'{ROOT}/pk/db.sqlite3'
_ = lambda path: path.replace(ROOT, '')


if __name__ == '__main__':
    # Download REMOTE_SOURCE to LOCAL_TMP
    dtstr = datetime.now().strftime('%Y-%m-%d')
    remote_source = REMOTE_SOURCE.format(dtstr=dtstr)
    log.info(f'Downloading database {remote_source}')
    subprocess.run(['scp', '-O', remote_source, LOCAL_TMP], check=True)
    # Delete LOCAL_BAK
    if exists(LOCAL_BAK):
        log.info(f'Deleting {_(LOCAL_BAK)}')
        os.remove(LOCAL_BAK)
    # Move LOCAL_DEST to LOCAL_BAK
    if exists(LOCAL_DEST):
        log.info(f'Moving {_(LOCAL_DEST)} to {_(LOCAL_BAK)}')
        os.rename(LOCAL_DEST, LOCAL_BAK)
    # Move LOCAL_TMP to LOCAL_DEST
    log.info(f'Moving {_(LOCAL_TMP)} to {_(LOCAL_DEST)}')
    os.rename(LOCAL_TMP, LOCAL_DEST)
