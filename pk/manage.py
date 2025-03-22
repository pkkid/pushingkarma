#!/usr/bin/env python3
# encoding: utf-8
import os, sys, time
from django.core.management import execute_from_command_line
from os.path import abspath, dirname, exists, expanduser

PROJECT_DIR = dirname(dirname(abspath(__file__)))
SETTINGS = f'{PROJECT_DIR}/pk/settings.py'
MOUNT_CMD = expanduser('~/Sync/Scripts/mount-private.py')


if __name__ == "__main__":
    # Make sure settings exists
    if not exists(SETTINGS) and 'runserver' in sys.argv:
        time.sleep(0.3)
        os.system(MOUNT_CMD)
    # Start Django management
    sys.path.insert(0, PROJECT_DIR)
    os.environ['DJANGO_SETTINGS_MODULE'] = 'pk.settings'
    project_dir = dirname(__file__)
    if project_dir not in sys.path:
        sys.path.append(project_dir)
    execute_from_command_line(sys.argv)
