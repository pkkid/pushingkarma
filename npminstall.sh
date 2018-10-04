#!/bin/bash
# encoding: utf-8
if [ `npm list | grep -c fsevents` -eq 0 -o ! -d node_modules ]; then
    npm install fsevents --force --no-optional --no-package-lock
fi
npm install --no-optional --no-package-lock
