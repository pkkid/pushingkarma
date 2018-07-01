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
npm install -g gulp bower
npm install
bower install  # choose bootstrap 4.0.0-beta
gulp

# Run the development server
./manage.py runserver 0.0.0.0:8000
```


### Setup Production Environment
1. Create a new Ubuntu instance
2. Update ansible/inventory.ini with the IP address of the new instance
3. cd ansible && ansible-playbook -i inventory.ini playbook.yml


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
