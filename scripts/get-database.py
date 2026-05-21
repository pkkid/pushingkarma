#!/usr/bin/env python
"""
Get Database
Fetch the latest SQLite backup from Synology into the local project.
"""
import argparse, os, shlex, subprocess, sys
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


def list_backups(opts):
    """ List available backups on the remote server. """
    result = subprocess.run(f"ssh synology ls {q(BACKUP_DIR)}", shell=True, check=True, capture_output=True, text=True)
    for filename in sorted(result.stdout.splitlines()):
        print(filename)


def download_backup(opts):
    """ Download the backup for the given date string to the local project. """
    dtstr = opts.date or datetime.now().strftime('%Y-%m-%d')
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


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Fetch a SQLite backup from Synology.')
    parser.add_argument('--list', action='store_true', help='List available backups on the remote server.')
    parser.add_argument('--date', metavar='YYYY-MM-DD', help='Date of the backup to download (default: today).')
    opts = parser.parse_args()
    if opts.list: list_backups(opts)
    else: download_backup(opts)
