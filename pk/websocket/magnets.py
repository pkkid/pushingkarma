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
    
    def on_connect(self, request, websocket):
        log.info('Connected!')
    
    def on_receive_message(self, request, websocket, recvmsg):
        log.info('Recieved: %s', recvmsg)
        return recvmsg
    
    def on_send_message(self, request, websocket, sendmsg):
        log.info('Sending: %s', sendmsg)
        return sendmsg
