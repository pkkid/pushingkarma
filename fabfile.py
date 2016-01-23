#!/usr/bin/python
# encoding: utf-8
"""
Copyright (c) 2015 PushingKarma. All rights reserved.
"""
import os
from fabric.api import cd, env, put, run, sudo
from fabric.contrib.project import rsync_project

RSYNC_EXCLUDE = ('.DS_Store', '__pycache__', '.git', '*.sqlite3', '*.example', '*.db', 'secrets.py', 'fabfile.py')
env.hosts = ['pushingkarma.com']
env.directory = '/home/mjs7231/Projects/pushingkarma'
env.virtualenv = '/home/mjs7231/.virtualenvs/pushingkarma'
env.privatemount = '/home/mjs7231/Projects/'
env.key_filename = '/home/mjs7231/Private/ssh/mykey'


def _virtualenv(command):
    """ Run a virtualenv command. """
    with cd('%s/bin' % env.virtualenv):
        activate = 'source ./activate && source ./postactivate'
        run('%s && %s' % (activate, command))
        

def deploy_source():
    """ Copy source files (default rsync options: -pthrvz). """
    remote_dir = os.path.dirname(env.directory)
    rsync_project(remote_dir, exclude=RSYNC_EXCLUDE, delete=True, extra_opts='--quiet --links --omit-dir-times')
    run('rm %s/pk/settings/secrets.py' % env.directory)
    put('/home/mjs7231/Private/pushingkarma/secrets.py', '%s/pk/settings/secrets.py' % env.directory)


def pip_install():
    """ Update to the latest requirements.pip. """
    requirments = '%s/requirements.pip' % env.directory
    _virtualenv('pip install -qUr %s' % requirments)


def reload_apache():
    """ Reload the apache server. """
    sudo('service apache2 reload', shell=False)
    

def deploy():
    """ Deploy to production. """
    deploy_source()
    pip_install()
    reload_apache()
