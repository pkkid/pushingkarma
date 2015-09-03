#!/usr/bin/env python
# encoding: utf-8
"""
Copyright (c) 2015 PushingKarma. All rights reserved.
"""
from pk.utils import context, response


def overview(request, template='projects/projects.html'):
    data = context.core(menuitem='projects')
    return response(request, template, data)


def django_dbbackup(request, template='projects/django_dbbackup.html'):
    data = context.core(menuitem='projects')
    return response(request, template, data)


def jquery_wysiwym(request, template='projects/jquery_wysiwym.html'):
    data = context.core(menuitem='jquery_wysiwym')
    return response(request, template, data)


def pkmeter(request, template='projects/pkmeter.html'):
    data = context.core(menuitem='jquery_wysiwym')
    return response(request, template, data)


def pks_movie_database(request, template='projects/pks_movie_database.html'):
    data = context.core(menuitem='jquery_wysiwym')
    return response(request, template, data)
