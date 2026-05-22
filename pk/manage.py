#!/usr/bin/env python3
# encoding: utf-8
import os, sys, time
from django.conf import settings
from django.core.management import execute_from_command_line
from django.core.management.color import color_style
from os.path import abspath, basename, dirname, exists, expanduser, islink

PROJECTDIR = dirname(dirname(abspath(__file__)))
ENVFILE = f'{PROJECTDIR}/.env'
MOUNTCMD = expanduser('~/Projects/scripts/mount-private.py')
style = color_style()


def setup_python_path():
    """ Setup the Python path for the project. """
    sys.path.insert(0, PROJECTDIR)
    os.environ['DJANGO_SETTINGS_MODULE'] = 'pk.settings'
    projectdir = dirname(__file__)
    if projectdir not in sys.path:
        sys.path.append(projectdir)


def check_private_mount():
    """ Ensure private directory is mounted. """
    if not exists(ENVFILE) and 'runserver' in sys.argv:
        time.sleep(0.3)
        os.system(MOUNTCMD)


def check_notes_symlinks():
    """ Check if Notes static files are symlinked. """
    displayed_warning = False
    for bucket in settings.OBSIDIAN_BUCKETS:
        bucketdir = basename(settings.OBSIDIAN_BUCKETS[bucket]['path'])
        sourcedir = f'{settings.OBSIDIAN_BUCKETS[bucket]['path']}/_static'
        destdir = f'{PROJECTDIR}/public/static/notes/{bucketdir}'
        if not islink(destdir):
            if not displayed_warning:
                print(style.WARNING('\nWARNING: Obsidian static dir is not symlinked'))
                displayed_warning = True
            print(style.WARNING(f'Run: ln -s {sourcedir} {destdir}'))
    if displayed_warning:
        print()

    
if __name__ == "__main__":
    check_private_mount()
    setup_python_path()
    check_notes_symlinks()
    execute_from_command_line(sys.argv)
