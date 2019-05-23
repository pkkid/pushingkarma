# encoding: utf-8
# Redis Subscriber class to recieve and parse messages.
import json
from redsocks.subscriber import RedisSubscriber
from redsocks import utils
from pk import log


class MagnetsSubscriber(RedisSubscriber):
    """ Routes calls within specified facilities to their destined subscribers. """
    
    def on_connect(self, request, websocket):
        log.info('Connected websocket..')
        meta = self._meta()
        if meta['clients'] >= 1:
            metastr = json.dumps(meta)
            websocket.send(metastr)
            self.publish_message(metastr)
        for wid, data in self.client.hgetall('magnets').items():
            try:
                data = json.loads(data.decode())
                data['action'] = 'add'
                websocket.send(json.dumps(data).encode())
            except Exception as err:
                log.error(err, exc_info=True)
                self.client.hdel('magnets', wid)
    
    def on_receive_message(self, request, websocket, recvmsg):
        try:
            data = json.loads(utils.to_str(recvmsg))
            wid, cls, action = data.get('id'), data.get('cls'), data.get('action')
            if action in ('update', 'add') and cls == '' and wid:
                self.client.hset('magnets', wid, json.dumps(data))
            elif action == 'remove' and wid:
                self.client.hdel('magnets', wid)
        except Exception as err:
            log.error(err, exc_info=1)
        finally:
            return recvmsg
            
    def on_disconnect(self, request, websocket):
        log.info('Disconnected websocket.')
        meta = self._meta(-1)
        if meta['clients'] >= 1:
            self.publish_message(json.dumps(meta))
        super(MagnetsSubscriber, self).on_disconnect(request, websocket)

    def _meta(self, offset=0):
        response = self.client.execute_command('PUBSUB NUMSUB ws:broadcast:magnets')
        clients = 0
        if response and len(response) >= 2:
            clients = response[1]
        return {'action':'meta', 'clients':clients + offset}
