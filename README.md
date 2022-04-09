## PushingKarma Website Code
This is the core code running pushingkarma.com.  Feel free to borrow
some ideas for your own site.  If you find anything useful, by all
means let me know. :)

### Setup Dev Environment
```bash
sudo apt install ansible redis-server
sudo apt install build-essential curl libbz2-dev libffi-dev liblzma-dev \
  libncursesw5-dev libreadline-dev libsqlite3-dev libssl-dev libxml2-dev \
  libxmlsec1-dev llvm make python3-dev tk-dev wget xz-utils zlib1g-dev
asdf install
pip install -r pk/requirements.pip
npm install
npm run start
```

### Setup Production Environment
1. Create a new Ubuntu instance
2. Update `ansible/inventory.ini` with the IP address of the new instance
3. Run: `npm run deploy-full`

### License
Create Commons Attribution-ShareAlike 2.5 Generic (CC BY-SA 2.5) - 
https://creativecommons.org/licenses/by-sa/2.5/
