#!/usr/bin/env python3
# encoding: utf-8
import os, sys, time
from django.conf import settings
from django.core.management import execute_from_command_line
from django.core.management.color import color_style
from os.path import abspath, basename, dirname, exists, expanduser, islink

PROJECT_DIR = dirname(dirname(abspath(__file__)))
SETTINGS = f'{PROJECT_DIR}/pk/settings.py'
MOUNT_CMD = expanduser('~/Sync/Scripts/mount-private.py')
style = color_style()


def setup_python_path():
    """ Setup the Python path for the project. """
    sys.path.insert(0, PROJECT_DIR)
    os.environ['DJANGO_SETTINGS_MODULE'] = 'pk.settings'
    project_dir = dirname(__file__)
    if project_dir not in sys.path:
        sys.path.append(project_dir)


def check_private_mount():
    """ Ensure private directory is mounted. """
    if not exists(SETTINGS) and 'runserver' in sys.argv:
        time.sleep(0.3)
        os.system(MOUNT_CMD)


def check_notes_symlinks():
    """ Check if Notes static files are symlinked. """
    displayed_warning = False
    for bucket in settings.OBSIDIAN_BUCKETS:
        bucketdir = basename(settings.OBSIDIAN_BUCKETS[bucket]['path'])
        sourcedir = f'{settings.OBSIDIAN_BUCKETS[bucket]['path']}/_static'
        destdir = f'{PROJECT_DIR}/public/static/notes/{bucketdir}'
        if not islink(destdir):
            if not displayed_warning:
                print(style.WARNING('\nWARNING: Obsidian static dir is not symlinked'))
                displayed_warning = True
            print(style.WARNING(f'Run: ln -s {sourcedir} {destdir}'))
    if displayed_warning:
        print()

    
if __name__ == "__main__":
    setup_python_path()
    check_private_mount()
    check_notes_symlinks()
    execute_from_command_line(sys.argv)
