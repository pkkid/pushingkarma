# Deploy code to server
# https://docs.fabfile.org/en/latest/
# https://www.pyinvoke.org/
import getpass, invoke, keyring, os
from fabric import Connection
from os.path import abspath, dirname

DOCKER = '/usr/local/bin/docker'
DOCKERNAME = 'pushingkarma'
LOCALDIR = abspath(dirname(__file__))
REMOTEUSER = 'pkkid'
REMOTEHOST = 'pushingkarma.com'
REMOTEDIR = '~/pushingkarma'
UV = '/var/services/homes/pkkid/.local/bin/uv'


class MyConnection(Connection):
    """ Fabric Connection object. """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sudopw = None

    def mkdir(self, path, chown=None, chmod=None):
        """ Create the remote directory and set permissions. """
        print(f'Ensuring {path} exists')
        self.run(f'mkdir -p {path}')
        if chown:
            print(f'Setting ownership {chown} {path}')
            self.run(f'chown {chown} {path}')
        if chmod:
            print(f'Setting permissions {chmod} {path}')
            self.run(f'chmod {chmod} {path}')

    def rsync(self, localdir, remotredir, excludes=None):
        """ Rsync the local directory to the remote directory.
            -r  recurse into directories
            -l  copy symlinks as symlinks
            -t  preserve modification times
            -v  increase verbosity
            -O  omit directories from --times
            --copy-links  transform symlink into referent file/dir
            --checksum  skip based on checksum, not mod-time & size
            --delete  delete extraneous files from dest dirs
        """
        cmd = f'rsync -r {localdir} {REMOTEUSER}@{REMOTEHOST}:{remotredir} '
        cmd += '-rltvO --copy-links --checksum --delete '
        cmd += '--rsync-path="/usr/bin/rsync" '
        cmd += ' '.join([f'--exclude={x}' for x in excludes])
        print(cmd)
        self.local(cmd)
    
    def step(self, msg, color='#ff0'):
        r,g,b = tuple(int(x * 2, 16) for x in color.lstrip('#'))
        print(f'\n==> \033[38;2;{r};{g};{b}m{msg}\033[00m')
    
    def sudo(self, cmd, logcmd=False, **kwargs):
        """ Run a sudo command on the remote machine. """
        self.sudopw = keyring.get_password('pk', 'synologypw')
        if not self.sudopw:
            self.sudopw = getpass.getpass('[sudo] remote password: ')
            keyring.set_password('pk', 'synologypw', self.sudopw)
            self.validate_sudopw()
        responder = invoke.Responder(pattern=r'\[sudo\] password:', response=f'{self.sudopw}\n')
        kwargs.setdefault('watchers', []).append(responder)
        if logcmd is True: print(f'> {cmd}')
        super().sudo(cmd, **kwargs)
    
    def validate_sudopw(self):
        """ Validate and save the sudo password of the remote machine. """
        try:
            self.sudo('whoami', hide='both')
        except invoke.exceptions.Failure:
            keyring.delete_password('pk', 'synologypw')
            raise SystemExit('Remote sudo password is incorrect.')


def check_settings_exists(conn):
    """ Ensure private directory is mounted. """
    if not os.path.exists(f'{LOCALDIR}/pk/settings.py'):
        raise SystemExit('Settings file does not exist.')


def build_vue(conn):
    """ Sync project files and set the right permissions. """
    conn.step(f'Building Vue Project to {LOCALDIR}/pk/_dist')
    conn.local(f'rm -rf {LOCALDIR}/_static')
    conn.local(f'uv run {LOCALDIR}/pk/manage.py collectstatic --noinput')
    conn.local(f'rm -rf {LOCALDIR}/_dist')
    conn.local('npm run build')
    conn.local(f'rm -rf {LOCALDIR}/_static')


def rsync_to_remote(conn):
    """ Sync project files and set the right permissions. """
    conn.step(f'Rsyncing Project to {REMOTEDIR}')
    excludes = [
        '__pycache__', '*/.git/', '*/.venv/', '*/.vscode/',
        '*/node_modules/', '*/_logs/', '*/_static/',
        '*/static/notes/', '*.bak', '*.sqlite3*']
    conn.rsync(LOCALDIR, '~', excludes=excludes)


def setup_log_directory(conn):
    """ Make sure the logs directory exists and has the right permissions. """
    conn.step(f'Setup Logs Directory {REMOTEHOST}:{REMOTEDIR}/_logs')
    conn.mkdir(f'{REMOTEDIR}/_logs', chmod='775')
    conn.mkdir(f'{REMOTEDIR}/_logs/nginx', chmod='775')
    conn.mkdir(f'{REMOTEDIR}/_logs/supervisor', chmod='775')


def initialize_django(conn):
    """ Run the Django migrations and collect static files. """
    conn.step('Initilizing Django Application')
    with conn.cd(REMOTEDIR):
        conn.run(f'{UV} run {REMOTEDIR}/pk/manage.py migrate')


def build_docker_image(conn, start=True):
    """ Build the docker image and start it. """
    # Create the new docker image
    conn.step(f'Building Docker Image: {REMOTEDIR} {DOCKERNAME}')
    conn.sudo(f'{DOCKER} build -t {DOCKERNAME} -f {REMOTEDIR}/Dockerfile {REMOTEDIR}', logcmd=True)
    if start:
        # Remove the old docker image
        print(f'Remove Old Docker Image: {DOCKERNAME}')
        conn.sudo(f'{DOCKER} stop {DOCKERNAME} || true', logcmd=True)
        conn.sudo(f'{DOCKER} rm {DOCKERNAME} || true', logcmd=True)
        # Start the new docker image
        print(f'Starting Docker Image: {DOCKERNAME}')
        cmd = f'{DOCKER} run --name {DOCKERNAME} -d -p 8080:80/tcp'
        cmd += f' -v {REMOTEDIR}:/app:rw'
        cmd += '  -v /volume1/homes/pkkid/Sync/Notes:/notes:ro'
        cmd += f' -v {REMOTEDIR}/_logs/nginx:/var/log/nginx:rw'
        cmd += f' -v {REMOTEDIR}/_logs/supervisor:/var/log/supervisor:rw'
        cmd += f' {DOCKERNAME}'
        conn.sudo(cmd, logcmd=True)


def restart_docker_image(conn):
    """ Restart the docker image. """
    conn.step(f'Restarting Docker image: {DOCKERNAME}')
    conn.sudo(f'{DOCKER} restart {DOCKERNAME}')


def restart_services(conn):
    """ Restart the web services. """
    conn.step(f'Restarting Daphne and Nginx in container: {DOCKERNAME}')
    conn.sudo(f'{DOCKER} exec {DOCKERNAME} supervisorctl restart daphne', logcmd=True)
    conn.sudo(f'{DOCKER} exec {DOCKERNAME} nginx -s reload', logcmd=True)


@invoke.task
def deploy(ctx, full=False):
    conn = MyConnection(host=REMOTEHOST, user=REMOTEUSER)
    check_settings_exists(conn)
    conn.validate_sudopw()
    build_vue(conn)
    rsync_to_remote(conn)
    setup_log_directory(conn) if full else None
    initialize_django(conn) if full else None
    build_docker_image(conn) if full else None
    restart_services(conn) if not full else None
    print('\nDone.')
