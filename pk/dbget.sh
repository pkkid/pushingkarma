#!/bin/bash
cd "$(dirname "$0")"

LOCAL_FILENAME="db.sqlite3"
REMOTE_FILENAME="pushingkarma-$(date '+%Y-%m-%d').sqlite3"

echo "$(date '+%Y-%m-%d %H:%M:%S'): Downloading db from Kin $REMOTE_FILENAME"
scp -O synology:~/synology/Michael/Backup/PushingKarma/$REMOTE_FILENAME $LOCAL_FILENAME.tmp || exit 1
echo "$(date '+%Y-%m-%d %H:%M:%S'): Deleting $REMOTE_FILENAME.bak"
rm $LOCAL_FILENAME.bak
echo "$(date '+%Y-%m-%d %H:%M:%S'): Moving $REMOTE_FILENAME to $REMOTE_FILENAME.bak"
mv $LOCAL_FILENAME $LOCAL_FILENAME.bak
echo "$(date '+%Y-%m-%d %H:%M:%S'): Moving $LOCAL_FILENAME.tmp to $LOCAL_FILENAME"
mv $LOCAL_FILENAME.tmp $LOCAL_FILENAME