#!/usr/bin/env python3
"""
Link Projects
Link local development packages into the active Python site-packages.
"""
import os
import shlex
import subprocess

DJANGO_SEARCH = f"{os.path.expanduser('~')}/Projects/django-searchquery/django_searchquery"
SITE_PACKAGES = subprocess.check_output('uv run python -c "import site; print(site.getsitepackages()[0])"',
    shell=True, text=True).strip()
TARGET = f'{SITE_PACKAGES}/django_searchquery'
q = lambda path: shlex.quote(path)


if __name__ == '__main__':
    if not os.path.isdir(DJANGO_SEARCH):
        raise SystemExit(f'Directory does not exist {DJANGO_SEARCH}')
    print(f'Removing {TARGET}')
    subprocess.run(f"rm -rf {q(TARGET)}", shell=True, check=True)
    print(f'Linking {DJANGO_SEARCH}')
    subprocess.run(f"ln -s {q(DJANGO_SEARCH)} {q(SITE_PACKAGES)}",
        shell=True, check=True)
