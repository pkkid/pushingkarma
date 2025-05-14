#!/bin/bash
# For development, we often need to link these local projects into
# the virtual environment site-packages. This script does that.
DJANGO_SEARCH="$HOME/Projects/django-searchquery/django_searchquery"
SITE_PACKAGES=$(uv run python -c 'import site; print(site.getsitepackages()[0])')

if [ -d "$DJANGO_SEARCH" ]; then
  echo "Removing $SITE_PACKAGES/django_searchquery"
  rm -rf $SITE_PACKAGES/django_searchquery
  echo "Linking  $DJANGO_SEARCH"
  ln -s $DJANGO_SEARCH $SITE_PACKAGES/
else
  echo "Directory does not exist $DJANGO_SEARCH"
fi
