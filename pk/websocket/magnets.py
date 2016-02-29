#!/usr/bin/env python
# encoding: utf-8
"""
Redis Subscriber class to recieve and parse messages.
Copyright (c) 2015 PushingKarma. All rights reserved.
"""
from redsocks.subscriber import RedisSubscriber
from pk import log


class MagnetsSubscriber(RedisSubscriber):
    """ Routes calls within specified facilities to their destined subscribers. """
    pass
