#!/usr/bin/env python
"""
Get Database
Fetch the latest SQLite backup from Synology into the local project.
"""
import os, shlex, subprocess, sys
import logging as log
from datetime import datetime
from os.path import abspath, dirname, exists

logformat = '%(asctime)-.19s %(module)16s:%(lineno)-3s %(levelname)-7s %(message)s'
log.basicConfig(stream=sys.stdout, level=log.INFO, format=logformat)

ROOT = dirname(dirname(abspath(__file__)))
BACKUP_DIR = '/volume1/Synology/Michael/Backup/pushingkarma'
REMOTE_SOURCE = f'synology:{BACKUP_DIR}/pushingkarma-{{dtstr}}.sqlite3'
LOCAL_TMP = f'{ROOT}/pk/db.sqlite3.tmp'
LOCAL_BAK = f'{ROOT}/pk/db.sqlite3.bak'
LOCAL_DEST = f'{ROOT}/pk/db.sqlite3'
_ = lambda path: path.replace(ROOT, '')
q = lambda path: shlex.quote(path)


if __name__ == '__main__':
    # Download REMOTE_SOURCE to LOCAL_TMP
    dtstr = datetime.now().strftime('%Y-%m-%d')
    remote_source = REMOTE_SOURCE.format(dtstr=dtstr)
    log.info(f'Downloading database {remote_source}')
    subprocess.run(f"scp -O {q(remote_source)} {q(LOCAL_TMP)}", shell=True, check=True)
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
