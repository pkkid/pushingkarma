#!/usr/bin/env python3
"""
Start Dev Server
Stop conflicting dev ports, start the app, and open the local dev URL.
"""
import os, shlex, shutil, subprocess, sys, time

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(PROJECT_ROOT)

def kill_port(port):
    """ Try fuser first, fall back to lsof. """
    if shutil.which('fuser'):
        return subprocess.run(shlex.split(f'fuser -k {port}/tcp'), capture_output=True)
    result = subprocess.run(shlex.split(f'lsof -ti tcp:{port}'), capture_output=True, text=True)
    pids = result.stdout.split()
    if pids:
        subprocess.run(shlex.split(f"kill {' '.join(pids)}"), capture_output=True)


if __name__ == '__main__':
    try:
        for port in [5173, 8000]: kill_port(port)
        server = subprocess.Popen(shlex.split('npm run start'))
        time.sleep(2)
        subprocess.Popen(shlex.split('xdg-open http://localhost:5173/'),
            stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL, start_new_session=True)
        server.wait()
    except KeyboardInterrupt:
        server.terminate()
        sys.exit(0)
