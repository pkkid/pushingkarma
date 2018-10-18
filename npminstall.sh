#!/bin/bash
# encoding: utf-8
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"

# Force install fsevents just to stop the warnings
if [ `npm list | grep -c fsevents` -eq 0 -o ! -d node_modules ]; then
    npm install fsevents --force --no-optional --no-save --no-package-lock
fi
# Install packages.json
npm install --no-optional --no-package-lock
# Link gulp.js to virtualenv bin directory
ln -s $DIR/node_modules/gulp/bin/gulp.js ~/.virtualenvs/pk/bin/gulp
