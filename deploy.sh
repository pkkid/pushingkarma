#!/bin/bash
# encoding: utf-8
ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"
ANS="$ROOT/ansible"

if [ "$1" = "getdb" ]; then
  scp pushingkarma.com:~/pk/db.sqlite3 $ROOT/pk/
elif [ "$1" = "full" ]; then
  ( npm run build && cd $ANS && ansible-playbook -i inventory.ini playbook.yml )
elif [ "$1" = "build" ]; then
  ( npm run build && cd $ANS && ansible-playbook -i inventory.ini playbook.yml --tags=deploy )
else
  ( cd $ANS && ansible-playbook -i inventory.ini playbook.yml --tags=deploy )
fi
