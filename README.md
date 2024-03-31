## PushingKarma Website Code
This is the core code running pushingkarma.com.  Feel free to borrow
some ideas for your own site.  If you find anything useful, by all
means let me know.

### Setup Dev Environment
```bash
sudo apt install ansible redis-server
sudo apt install build-essential curl libbz2-dev libffi-dev liblzma-dev \
  libncursesw5-dev libreadline-dev libsqlite3-dev libssl-dev libxml2-dev \
  libxmlsec1-dev llvm make python3-dev tk-dev wget xz-utils zlib1g-dev
pyenv virtualenv 3.11 pk
pyenv local pk
pip install -r pk/requirements.pip

nvm install 16
nvm use 16
npm install
npm run start
```
REMEMBER: To make sure the Django dev server is running with DEBUG=True,
otherwise static files will not be served when running `npm run start` and
you will waste your day trying to figure it out.


### Setup Production Environment
1. Create a new Ubuntu instance
2. Update domain server DNS entry to point your domain to the instance
3. Wait for DNS resolution to update and ability to ssh in by domain name
4. Update `ansible/inventory.ini` with the IP address of the new instance
5. Make sure secrets.py is mounted or accessible
6. Run: `npm run deploy-full`

### License
Create Commons Attribution-ShareAlike 2.5 Generic (CC BY-SA 2.5) - 
https://creativecommons.org/licenses/by-sa/2.5/
