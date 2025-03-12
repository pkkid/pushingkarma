#!/bin/bash
cd "$(dirname "$0")"

LOCAL_FILENAME="db.sqlite3"
REMOTE_FILENAME="pushingkarma-$(date '+%Y-%m-%d').sqlite3"

echo "$(date '+%Y-%m-%d %H:%M:%S'): Writing db to Kin $REMOTE_FILENAME"
cp $LOCAL_FILENAME /volume1/Synology/Michael/Backup/PushingKarma/$REMOTE_FILENAME