#!/usr/bin/env python
# encoding: utf-8
"""
Copyright (c) 2015 PushingKarma. All rights reserved.
"""
import os, sys
from django.core.management import execute_from_command_line


if __name__ == "__main__":
    project_dir = os.path.dirname(__file__)
    if project_dir not in sys.path:
        sys.path.append(project_dir)
    execute_from_command_line(sys.argv)
