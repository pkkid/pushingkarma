#!/usr/bin/env python
# encoding: utf-8
"""
Support more redis operations than standard Django cache.
Reference: http://redis.io/commands/<COMMAND>
Copyright (c) 2015 PushingKarma. All rights reserved.
"""
from redis_cache import RedisCache


class CompleteRedisCache(RedisCache):
    
    def __getattr__(self):
        raise AttributeError('Creating new attributes is not allowed.')
    
    # def hdel(self, name, *keys):
    #     return self._client.hdel(name, *keys)
    # 
    # def hgetall(self, name):
    #     return self._client.hgetall(name)
    # 
    # def hset(self, name, key, value):
    #     return self._client.hset(name, key, value)
