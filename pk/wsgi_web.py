# encoding: utf-8
import os
import gevent.socket
import redis.connection
redis.connection.socket = gevent.socket
os.environ.update(DJANGO_SETTINGS_MODULE='pk.settings.settings')
from redsocks.server import uWSGIWebsocketServer
application = uWSGIWebsocketServer()
