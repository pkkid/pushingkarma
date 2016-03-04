#!/usr/bin/env python
# encoding: utf-8
"""
Redis Subscriber class to recieve and parse messages.
Copyright (c) 2015 PushingKarma. All rights reserved.
"""
import json
from redsocks.subscriber import RedisSubscriber
from pk import log


class MagnetsSubscriber(RedisSubscriber):
    """ Routes calls within specified facilities to their destined subscribers. """
    
    def on_connect(self, request, websocket):
        log.info('Connected!')
        for _id, data in self.client.hgetall('magnets').items():
            try:
                data = json.loads(data.decode())
                data['action'] = 'add'
                websocket.send(json.dumps(data))
            except Exception as err:
                log.error(err)
                self.client.hdel('magnets', _id)
    
    def on_receive_message(self, request, websocket, recvmsg):
        try:
            data = json.loads(recvmsg.decode())
            _id, _cls, _action = data.get('id'), data.get('cls'), data.get('action')
            if _action in ('update', 'add') and _cls == '' and _id:
                self.client.hset('magnets', _id, json.dumps(data))
            elif _action == 'remove' and _id:
                self.client.hdel('magnets', _id)
        finally:
            return recvmsg
