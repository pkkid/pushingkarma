## PushingKarma Website Code
This is the core code running pushingkarma.com.  Feel free to borrow
some ideas for your own site.  If you find anything useful, by all
means let me know. :)

### Setup Dev Environment
```bash
# Create a virtualenv environment
sudo apt install virtualenvwrapper redis-server
mkvirtualenv --python=/usr/bin/python3
pip install -r pk/requirements.pip

# Setup npm, gulp and bower
sudo apt install ruby ruby-dev nodejs npm
sudo su -c 'gem install sass'
npm install -g gulp-cli
./npminstall.sh
gulp build

# Run the development server
./manage.py runserver 0.0.0.0:8000
```

### Setup Production Environment
1. Create a new Ubuntu instance
2. Update `ansible/inventory.ini` with the IP address of the new instance
3. Run: `./deploy setup`

### License
Create Commons Attribution-ShareAlike 2.5 Generic (CC BY-SA 2.5) - 
https://creativecommons.org/licenses/by-sa/2.5/
