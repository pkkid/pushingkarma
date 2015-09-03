"""
Deploy code from the BitBucket repo on the production server.
"""
import os
from fabric.api import cd, env, run, sudo
from fabric.contrib.project import rsync_project

RSYNC_EXCLUDE = ('.DS_Store', '.hg', '*.pyc', '*.example', '*.db', 'fabfile.py', "collectstatic")
env.hosts = ["pushingkarma.com"]
env.directory = '/home/mjs7231/Projects/pushingkarma'
env.virtualenv = '/home/mjs7231/.virtualenvs/pushingkarma'
env.privatemount = '/home/mjs7231/Projects/'


def virtualenv(command):
    """ Run a virtualenv command. """
    with cd('%s/bin' % env.virtualenv):
        activate = 'source ./activate && source ./postactivate'
        run('%s && %s' % (activate, command))


def collectstatic():
    """ Collect static files. """
    run('mkdir -p %s/collectstatic' % env.directory)
    virtualenv('%s/manage.py collectstatic --clear --link --noinput -v0' % env.directory)


def copy_source():
    """ Copy source files (default rsync options: -pthrvz). """
    remote_dir = os.path.dirname(env.directory)
    rsync_project(remote_dir, exclude=RSYNC_EXCLUDE, delete=True, extra_opts="--quiet --links --omit-dir-times")


def pip_install():
    """ Update to the latest requirements.pip. """
    requirments = '%s/environment/requirements.pip' % env.directory
    virtualenv('pip install -qr %s' % requirments)


def pip_update():
    """ Update to the latest requirements.pip. """
    requirments = '%s/environment/requirements.pip' % env.directory
    virtualenv('pip install -U -qr %s' % requirments)


def reload_apache():
    """ Reload the apache server. """
    sudo('service apache2 reload', shell=False)


def restart_apache():
    """ Reload the apache server. """
    sudo('service apache2 restart', shell=False)


def update_source():
    """ Update the project source. """
    with cd(env.directory):
        run('hg pull')
        run('hg update')


def wysiwym_update():
    """ Update jquery-wysiwym source. """
    with cd('/home/mjs7231/Projects/jquery-wysiwym'):
        run('hg pull')
        run('hg update')


##############################
#  Deploy to Production
##############################

def deploy():
    """ Deploy to production. """
    copy_source()
    pip_install()
    wysiwym_update()
    collectstatic()
    reload_apache()
