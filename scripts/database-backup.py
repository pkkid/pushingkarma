#!/usr/bin/env python
# Database Backup
# Saves a backup of the current database to Synology
import shutil, sys
import logging as log
from datetime import datetime, timedelta
from glob import glob
from os.path import dirname, abspath
from pathlib import Path

logformat = '%(asctime)-.19s %(module)16s:%(lineno)-3s %(levelname)-7s %(message)s'
log.basicConfig(stream=sys.stdout, level=log.INFO, format=logformat)

ROOT = dirname(dirname(abspath(__file__)))
LOCAL_SOURCE = f'{ROOT}/pk/db.sqlite3'
BACKUP_DIR = '/volume1/Synology/Michael/Backup/pushingkarma'
REMOTE_DEST = f'{BACKUP_DIR}/pushingkarma-{{dtstr}}.sqlite3'
_ = lambda path: path.replace(ROOT, '')


def cleanup_old_backups():
    """ Delete backups older than 2 weeks, except those from the 1st of each month. """
    cutoff_date = datetime.now() - timedelta(weeks=2)
    pattern = f'{BACKUP_DIR}/pushingkarma-*.sqlite3'
    for backup_file in glob(pattern):
        # Extract date from filename (format: pushingkarma-YYYY-MM-DD.sqlite3)
        filename = Path(backup_file).name
        date_str = filename.replace('pushingkarma-', '').replace('.sqlite3', '')
        backup_date = datetime.strptime(date_str, '%Y-%m-%d')
        # Keep if newer than 2 weeks OR if it's from the 1st of the month
        is_old = backup_date < cutoff_date
        is_monthly_archive = backup_date.day == 1
        if is_old and not is_monthly_archive:
            log.info(f'Deleting old backup: {filename}')
            Path(backup_file).unlink()


if __name__ == '__main__':
    dtstr = datetime.now().strftime('%Y-%m-%d')
    remote_dest = REMOTE_DEST.replace('{dtstr}', dtstr)
    log.info(f'Saving {_(LOCAL_SOURCE)} to {remote_dest}')
    shutil.copy(LOCAL_SOURCE, remote_dest)
    log.info('Cleaning up old backups...')
    cleanup_old_backups()
