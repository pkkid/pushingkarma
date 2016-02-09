#!/usr/bin/python
# encoding: utf-8
"""
Copyright (c) 2015 PushingKarma. All rights reserved.
"""
import os
from fabric.api import cd, env, local, put, run, sudo
from fabric.contrib.project import rsync_project

RSYNC_EXCLUDE = ('.DS_Store', '__pycache__', '.git', '*.sqlite3', '*.example', '*.db', 'secrets.py', 'fabfile.py')
env.hosts = ['162.243.98.231']
env.directory = '/home/mjs7231/Projects/pushingkarma'
env.virtualenv = '/home/mjs7231/.virtualenvs/pushingkarma'
env.privatemount = '/home/mjs7231/Projects/'
env.key_filename = '/home/mjs7231/Private/ssh/mykey'


def _virtualenv(command):
    """ Run a virtualenv command. """
    with cd('%s/bin' % env.virtualenv):
        activate = 'source ./activate && source ./postactivate'
        run('%s && %s' % (activate, command))
        

def build_static():
    """ Build local static files to be uploaded. """
    local('cd /home/mjs7231/Projects/pushingkarma && /home/mjs7231/Sources/node_modules/bin/gulp default')


def deploy_source():
    """ Copy source files (default rsync options: -pthrvz). """
    local = env.directory
    remote = os.path.dirname(env.directory)
    rsync_project(local_dir=local, remote_dir=remote, exclude=RSYNC_EXCLUDE, delete=True, extra_opts='--quiet --links --omit-dir-times')
    run('rm -f %s/pk/settings/secrets.py' % env.directory)
    put('/home/mjs7231/Private/pushingkarma/secrets.py', '%s/pk/settings/secrets.py' % env.directory)
    _virtualenv('django-admin.py collectstatic --link --noinput --verbosity=0')


def pip_install():
    """ Update to the latest requirements.pip. """
    requirments = '%s/conf/requirements.pip' % env.directory
    _virtualenv('pip install -qUr %s' % requirments)


def restart_server():
    """ Reload the http server. """
    sudo('service uwsgi restart', shell=False)
    sudo('service nginx restart', shell=False)
    

def deploy():
    """ Deploy to production. """
    build_static()
    deploy_source()
    pip_install()
    restart_server()