#!/usr/bin/env python
# encoding: utf-8
"""
Copyright (c) 2015 PushingKarma. All rights reserved.
"""


class Bunch(dict):

    def __getattr__(self, item):
        try:
            return self.__getitem__(item)
        except KeyError:
            return None

    def __setattr__(self, item, value):
        return self.__setitem__(item, value)


def core(request, **kwargs):
    if '_core' not in request:
        data = Bunch(**kwargs)
        request._core = data
    return request._core
