## PushingKarma Website Code
This is the core code running pushingkarma.com.  Feel free to borrow
some ideas for your own site.  If you find anything useful, by all
means let me know. :)

### Requirements
* Python3, Pip, Virtualenv, Fabric
* Npm, Bower, Sass, Autoprefixer, Gulp

### Installation
```bash
# Create Python Virtualenv
> git clone git@github.com:mjs7231/pushingkarma.git ~/Projects/pushingkarma
> mkvirtualenv --python=/usr/bin/python3 -a /home/mjs7231/Projects/pushingkarma pk
> rm ~/.virtualenvs/pk/bin/postactivate
> ln -s ~/Projects/pushingkarma/conf/postactivate ~/.virtualenvs/pk/bin/postactivate
> workon pk

# Install Python Requirements
> pip install -U pip
> pip install -r ~/Projects/pushingkarma/conf/requirements.pip
```

### Dev Environment
```bash
# Install Development Utilities
> sudo su -c "gem install sass"
> sudo ln -s /usr/bin/nodejs ~/.local/bin/node
> npm install -g gulp bower
> npm install
> bower install    # choose bootstrap 4 and jquery 3
> gulp

# Update Nodejs to latest version (if hitting errors)
> curl -sL https://deb.nodesource.com/setup_4.x | sudo -E bash -
> sudo apt-get install -y nodejs
> npm rebuild node-sass

# Install Redis and django-redsocks
> sudo apt-get install redis
> git clone git@github.com:pkkid/django-redsocks.git ~/Projects/django-redsocks
> ln -s ~/Projects/django-redsocks/redsocks ~/.virtualenvs/pk/lib/python3.5/site-packages/

# Kickstart the Database
> django-admin migrate
```

-----
### License

Create Commons Attribution-ShareAlike 2.5 Generic (CC BY-SA 2.5)
https://creativecommons.org/licenses/by-sa/2.5/

* You are free to share - copy and redistribute the material in any medium
or format. You are free to adapt - remix, transform, and build upon the
material for any purpose, even commercially. The licensor cannot revoke these
freedoms as long as you follow the license terms.

* You must provide attribution - You must give appropriate credit, provide a
link to the license, and indicate if changes were made. You may do so in any
reasonable manner, but not in any way that suggests the licensor endorses you
or your use.
* You must ShareAlike - If you remix, transform, or build upon the material,
you must distribute your contributions under the same license as the original.

No additional restrictions - You may not apply legal terms or technological
measures that legally restrict others from doing anything the license permits.

You do not have to comply with the license for elements of the material in the
public domain or where your use is permitted by an applicable exception or
limitation. No warranties are given. The license may not give you all of the 
permissions necessary for your intended use. For example, other rights such as
publicity, privacy, or moral rights may limit how you use the material.

[![Analytics](https://ga-beacon.appspot.com/UA-87461-7/pushingkarma/home)](https://github.com/igrigorik/ga-beacon)
