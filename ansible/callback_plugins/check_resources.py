# Checks the Secrets file is mounted
from os.path import dirname, isfile, join
from ansible.plugins.callback import CallbackBase

PROJECT_DIR = dirname(dirname(dirname(__file__)))

class CallbackModule(CallbackBase):
    def __init__(self, *args, **kwargs):
        secrets = join(PROJECT_DIR, 'pk/settings/secrets.py')
        dist = join(PROJECT_DIR, 'pk/_dist/index.html')
        if not isfile(secrets):
            raise Exception(f'Secrets not present: {secrets}')
        if not isfile(dist):
            raise Exception(f'Distribution files not present: {dist}')
