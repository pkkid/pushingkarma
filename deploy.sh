#!/bin/bash
# encoding: utf-8
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"
ANS="$DIR/ansible"

if [ "$1" = "getdb" ]; then
   scp pushingkarma.com:~/pk/db.sqlite3 $DIR
elif [ "$1" = "full" ]; then
   ansible-playbook -i $ANS/inventory.ini $ANS/playbook.yml
else
  ansible-playbook -i $ANS/inventory.ini $ANS/playbook.yml --tags=deploy
fi
