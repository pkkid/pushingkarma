# Checks the Secrets file is mounted
from os.path import dirname, isfile, join
from ansible.plugins.callback import CallbackBase

PROJECT_DIR = dirname(dirname(dirname(__file__)))

class CallbackModule(CallbackBase):
    def __init__(self, *args, **kwargs):
        # Check secrets file is present
        secrets = join(PROJECT_DIR, 'pk/settings/secrets.py')
        if not isfile(secrets):
            raise Exception(f'Secrets not present.\nPlease run: "addkeys.sh"')
        # Check Distribution files are present
        dist = join(PROJECT_DIR, 'pk/_dist/index.html')
        if not isfile(dist):
            raise Exception(f'Development files present.\n'
                'Please stop the dev server and run: "npm run build"')
        # Check _dist directory contains production files
        appjs = join(PROJECT_DIR, 'pk/_dist/pushingkarma/js/app.js')
        if isfile(appjs):
            raise Exception(f'Distribution files not present.\n'
                'Please stop the dev server and run: "npm run build"')
