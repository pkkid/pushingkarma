#!/usr/bin/env python3
# encoding: utf-8
import os, sys
from django.core.management import execute_from_command_line
from os.path import abspath, dirname


if __name__ == "__main__":
    sys.path.insert(0, dirname(dirname(abspath(__file__))))
    os.environ['DJANGO_SETTINGS_MODULE'] = 'pk.settings'
    project_dir = dirname(__file__)
    if project_dir not in sys.path:
        sys.path.append(project_dir)
    execute_from_command_line(sys.argv)
