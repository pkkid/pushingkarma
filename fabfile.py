# Deploy code to server
# https://docs.fabfile.org/en/latest/
# https://www.pyinvoke.org/
import getpass
from fabric import Connection
from os.path import abspath, dirname
from invoke import Responder
from invoke import exceptions, task

LOCALDIR = abspath(dirname(__file__))
DOCKERNAME = 'pushingkarma'
DOCKERDIR = '/volume1/docker/pushingkarma'
REMOTEUSER = 'pkkid'
REMOTEHOST = 'synology'
REMOTEDIR = '~/pkkid/pk'
UV = '~/.local/bin/uv'


class MyConnection(Connection):
    """ Fabric Connection object. """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sudopw = None

    def rsync(self, localdir, remotredir, excludes=None):
        """ Rsync the local directory to the remote directory. """
        cmd = [f'rsync -r {localdir} {self.original_host}:{remotredir}',
            '-rltvO', '--copy-links', '--checksum', '--delete']
        cmd += [f'--exclude={x}' for x in excludes]
        self.local(' '.join(cmd))
    
    def step(self, msg, color='#ff0'):
        r,g,b = tuple(int(x * 2, 16) for x in color.lstrip('#'))
        print(f'\n==> \033[38;2;{r};{g};{b}m{msg}\033[00m')
    
    def sudo(self, *args, **kwargs):
        """ Run a sudo command on the remote machine. """
        if not self.sudopw:
            self.sudopw = getpass.getpass('[sudo] remote password: ')
            self.validate_sudopw()
        sudopass = Responder(pattern=r'\[sudo\] password:', response=f'{self.sudopw}\n')
        kwargs.setdefault('watchers', []).append(sudopass)
        super().sudo(*args, **kwargs)
    
    def validate_sudopw(self):
        """ Validate and save the sudo password of the remote machine. """
        try:
            self.sudo('whoami', hide='both')
        except exceptions.Failure:
            raise SystemExit('Remote sudo password is incorrect.')


def build_vue(conn):
    """ Sync project files and set the right permissions. """
    conn.step(f'Building Vue Project to {LOCALDIR}/pk/_dist')
    conn.local('npm run build')


def rsync_to_remote(conn):
    """ Sync project files and set the right permissions. """
    conn.step(f'Rsyncing Project to {REMOTEHOST}:{REMOTEDIR}')
    excludes = ['__pycache__', '_static', '*.sqlite3*', '*.bak']
    conn.rsync(f'{LOCALDIR}/pk', REMOTEDIR, excludes=excludes)


def initialize_django(conn):
    """ Run the Django migrations and collect static files. """
    conn.step('Initilizing Django Application')
    managepy = f'{REMOTEDIR}/pk/manage.py'
    conn.django_command(managepy, UV, 'migrate')
    conn.django_command(managepy, UV, 'collectstatic --noinput')


def setup_log_directory(conn):
    """ Make sure the logs directory exists and has the right permissions. """
    conn.step(f'Setting Up Logs Directory {REMOTEHOST}:{REMOTEDIR}/_logs')
    conn.mkdir(f'{REMOTEDIR}/_logs', chown=f'{REMOTEUSER}:www-data', chmod='775')


def set_permissions(conn):
    """ Set permissions on the remote files. """
    conn.step('Setting Remote Permissions')
    usergroup = f'{REMOTEUSER}:www-data'
    conn.set_permissions(REMOTEDIR, usergroup, dchmod='775', fchmod='664')
    conn.run(f'chmod 774 {REMOTEDIR}/pk/manage.py')


def build_docker_image(conn, start=True):
    """ Build the docker image and start it. """
    conn.step(f'Building Docker Image: {REMOTEDIR} {DOCKERNAME}')
    with conn.cd(REMOTEDIR):
        conn.sudo(f'docker build -t {DOCKERNAME} -f Dockerfile .')
        if start:
            print(f'Starting Docker Image: {DOCKERNAME}')
            cmd = f'docker run {DOCKERNAME} --name {DOCKERNAME}'
            cmd += ' -d -p 8080:80/tcp -v {DOCKERDIR}:/app:rw'
            conn.sudo(cmd)


def restart_docker_image(conn):
    """ Restart the docker image. """
    conn.step(f'Restarting Docker image: {DOCKERNAME}')
    conn.sudo(f'docker restart {DOCKERNAME}')


@task
def deploy(ctx, full=False):
    conn = MyConnection(host=REMOTEHOST, user=REMOTEUSER)
    conn.validate_sudopw()
    build_vue(conn)
    rsync_to_remote(conn)
    setup_log_directory(conn)
    initialize_django(conn)
    set_permissions(conn)
    if (full): build_docker_image(conn)
    else: restart_docker_image(conn)
