# encoding: utf-8
import hashlib, time, traceback
from django.conf import settings
from django.core.cache import cache
from django.utils.log import AdminEmailHandler
from rest_framework.exceptions import AuthenticationFailed
from pk import log


class CustomEmailHandler(AdminEmailHandler):

    def __init__(self, *args, **kwargs):
        super(CustomEmailHandler, self).__init__(*args, **kwargs)
        self.timeout = 600          # Timeout before sending second email
        self.maxcount = 100         # Max hits before sending second email
        self.ignore = [             # Exception classes to ignore
            AuthenticationFailed,   # Rest Framework AuthenticationFailed
        ]
    
    def emit(self, record):
        if self._check_send_email(record):
            super(CustomEmailHandler, self).emit(record)
    
    def _check_send_email(self, record):
        """ Return True if count is 0, we reached max_count, or timeout reached.
            Otherwise just increment the count.
        """
        now = time.time()
        etype, evalue, tb = record.exc_info
        if etype in self.ignore:
            log.info('Not sending excpetion email; ignored')
            return False
        hashkey = f'exc_{self._get_ehash(tb)}'
        count, timeout = self._get_cached(hashkey)
        newcount = count + 1
        if count == 0 or newcount >= self.maxcount or now >= timeout:
            ename = etype.__name__
            estr = str(evalue) or '--'
            record.getMessage = lambda: f'[{newcount}x] {ename}: {estr}'
            self._set_cached(hashkey, 1, now + self.timeout)
            if settings.DEBUG:
                log.info('Not sending excpetion email; DEBUG=True')
                return False
            return True
        else:
            log.info(f'Not sending excpetion email; count={newcount}')
        self._set_cached(hashkey, newcount, timeout)
        return False

    def _get_ehash(self, tb):
        hash = hashlib.md5()
        for frame in traceback.extract_tb(tb):
            hash.update(str(frame[0]).encode())  # file path
            hash.update(str(frame[1]).encode())  # file lineno
        return hash.hexdigest()
    
    def _get_cached(self, hashkey):
        count, timeout = cache.get(hashkey, '0:0').split(':')
        return int(count), int(timeout)
    
    def _set_cached(self, hashkey, count, timeout):
        value = f'{count}:{int(timeout)}'
        cache.set(hashkey, value, self.timeout)
