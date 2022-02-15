## PushingKarma Website Code
This is the core code running pushingkarma.com.  Feel free to borrow
some ideas for your own site.  If you find anything useful, by all
means let me know. :)

### Setup Dev Environment
```bash
# Create Python virtualenv environment
sudo apt install ansible redis-server virtualenvwrapper
mkvirtualenv --python=/usr/bin/python3 pk
pip install -r pk/requirements.pip
pk/manage.py migrate
pk/manage.py runserver 0.0.0.0:8000

# Setup NPM and Vue
# Last tested with node=v10.24.1 npm=v8.3.1
# You can use nvm to get the right version of node.
sudo apt install npm
npm install
npm run vue-build
npm run start
```

### Setup Production Environment
1. Create a new Ubuntu instance
2. Update `ansible/inventory.ini` with the IP address of the new instance
3. Run: `npm run deploy-full`

### License
Create Commons Attribution-ShareAlike 2.5 Generic (CC BY-SA 2.5) - 
https://creativecommons.org/licenses/by-sa/2.5/
