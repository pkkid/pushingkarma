# PushingKarma Website
This is the core code running pushingkarma.com. Feel free to borrow some ideas
for your own site. If you find anything useful, by all means let me know.

## Development Setup
```bash
# Clone the repo
git git@github.com:pkkid/pushingkarma.git
cd pushingkarma

# Create Python virtualenv & install requirements
pyenv install 3.11
pyenv virtualenv 3.11 pk
pyenv local pk
pip install -r pk/requirements.txt

# Install node v20.11 (lts)
nvm install 20.11
nvm use 20.11
npm install

# Start the Django and Vue servers together
# Django http://localhost:8000/
# Vue http://localhost:5173/ (use this one)
npm run start
```

#### Other Useful Package Commands
```bash
npm run getdb          # Gets the Production sqlite db from http://pdash.nasuni.net/db.sqlite3
npm run start          # Starts Django and Vue servers together
npm run django         # Watch and reload Django when files changed
npm run vue            # Watch and reload Vue when files changed
npm run build          # Compile and Minify for Production
npm run eslint         # Lint with [ESLint](https://eslint.org/)
```

#### References
* [Volar Extension for VSCode](https://marketplace.visualstudio.com/items?itemName=Vue.volar) (disable Vetur)
* [Vite Configuration Reference](https://vitejs.dev/config/)
* [VueUse](https://vueuse.org/) (Vue composition utilities)
* [Material Symbols](https://fonts.google.com/icons?icon.set=Material+Symbols)
