#!/usr/bin/env python3
"""
Install Depenedencies
Install project dependencies for the main repo or a git worktree checkout.
"""
import os, shutil, subprocess

MAINREPO = '/home/pkkid/Projects/pushingkarma'
PROJECTROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(PROJECTROOT)


if __name__ == '__main__':
    gitcommon = subprocess.run('git rev-parse --git-common-dir',
        shell=True, capture_output=True, text=True).stdout.strip()
    isworktree = gitcommon != '.git'
    print('Running setup for main repo')
    subprocess.run('npm install', shell=True)
    subprocess.run('uv sync --all-extras', shell=True)
    if isworktree:
        envpath = f'{PROJECTROOT}/.env'
        if not os.path.exists(envpath):
            os.symlink(f'{MAINREPO}/.env', envpath)
        dbpath = f'{PROJECTROOT}/pk/db.sqlite3'
        if not os.path.exists(dbpath):
            shutil.copy(f'{MAINREPO}/pk/db.sqlite3', dbpath)
