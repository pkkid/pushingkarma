#!/bin/bash
# encoding: utf-8
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"
cd $DIR/ansible
if [ "$1" = "full" ]; then
   ansible-playbook -i inventory.ini playbook.yml
else
  ansible-playbook -i inventory.ini playbook.yml --tags=deploy
fi
cd -
