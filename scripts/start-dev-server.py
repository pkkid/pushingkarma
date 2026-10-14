#!/usr/bin/env python3
"""
Start Dev Server
Stop conflicting dev ports and start the app for this checkout or a given worktree.
All checkouts serve the same ports, so any running dev server is stopped first.
"""
import argparse, os, shlex, shutil, subprocess

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PORTS = [5173, 8000]


def kill_port(port):
    """ Try fuser first, fall back to lsof. """
    if shutil.which('fuser'):
        return subprocess.run(shlex.split(f'fuser -k {port}/tcp'), capture_output=True)
    result = subprocess.run(shlex.split(f'lsof -ti tcp:{port}'), capture_output=True, text=True)
    pids = result.stdout.split()
    if pids:
        subprocess.run(shlex.split(f"kill {' '.join(pids)}"), capture_output=True)


def needs_setup(checkout):
    """ True when the checkout is missing its env, database or packages, or the lockfile changed. """
    paths = [f'{checkout}/{path}' for path in ['.env', 'pk/db.sqlite3', '.venv', 'node_modules']]
    lockfile, installed = f'{checkout}/package-lock.json', f'{checkout}/node_modules/.package-lock.json'
    stale = os.path.exists(installed) and os.path.getmtime(lockfile) > os.path.getmtime(installed)
    return stale or not all(os.path.lexists(path) for path in paths)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Start or stop the Django and Vue dev servers.')
    parser.add_argument('checkout', nargs='?', default=PROJECT_ROOT, help='Checkout to serve (default: this one).')
    parser.add_argument('--stop', action='store_true', help='Stop the running dev server and exit.')
    opts = parser.parse_args()
    for port in PORTS: kill_port(port)
    if opts.stop:
        print('Dev server stopped.')
        raise SystemExit(0)
    # Worktrees share no packages, env or database with the main checkout; set them up when missing
    checkout = subprocess.run(['git', '-C', opts.checkout, 'rev-parse', '--show-toplevel'],
        capture_output=True, text=True, check=True).stdout.strip()
    if needs_setup(checkout):
        print('Installing dependencies…', flush=True)
        subprocess.run([f'{checkout}/scripts/install-dependencies.py'], check=True)
    # The main .env links into ~/Private/Secrets, which is only there while that folder is mounted
    if not os.path.exists(f'{checkout}/.env'):
        raise SystemExit(f'Cannot start: {checkout}/.env is missing or links to a file that is not there '
            f'({os.path.realpath(f"{checkout}/.env")}). Is ~/Private mounted?')
    # Replace this process with npm so a stop signal reaches the servers directly
    print(f'Starting dev server for {checkout}', flush=True)
    os.chdir(checkout)
    os.execvp('npm', ['npm', 'run', 'start'])
