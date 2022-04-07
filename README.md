## PushingKarma Website Code
This is the core code running pushingkarma.com.  Feel free to borrow
some ideas for your own site.  If you find anything useful, by all
means let me know. :)

### Setup Dev Environment
```bash
# Create Python virtualenv environment
# Create Python virtualenv environment
sudo apt install ansible redis-server virtualenvwrapper
mkvirtualenv pk
pip install -r pk/requirements.pip
cd ~/Projects/pushingkarma/pk/settings && ln -s <secrets> .
pk/manage.py migrate
pk/manage.py runserver 0.0.0.0:8000

# Setup NPM and Vue
# Last tested with node=v14.19.1 npm=v8.6.0
# You can use nvm to get the right version of node.
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.1/install.sh | bash
nvm install 10.24.1
nvm use 10.24.1
cd ~/Projects/pushingkarma && npm install
cd ~/Projects/pushingkarma && npm run vue-build
cd ~/Projects/pushingkarma && npm run start


# New ASDF Setup
# After installing asdf
asdf install
```

### Setup Production Environment
1. Create a new Ubuntu instance
2. Update `ansible/inventory.ini` with the IP address of the new instance
3. Run: `npm run deploy-full`

### License
Create Commons Attribution-ShareAlike 2.5 Generic (CC BY-SA 2.5) - 
https://creativecommons.org/licenses/by-sa/2.5/
