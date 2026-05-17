# PushingKarma Website
This is the core code running pushingkarma.com. Feel free to borrow some ideas
for your own site. If you find anything useful, by all means let me know.

## Development Setup

1. Install NVM: https://github.com/nvm-sh/nvm
2. Install UV: https://github.com/astral-sh/uv

```bash
# Setup JS and Python environments
cd pushingkarma             # Change cwd
cp ~/Private/Secrets/pushingkarma/.env.development .env
cp ~/Private/Secrets/pushingkarma/.env.production .
nvm install                 # Install npm
npm install                 # Setup JS env
uv sync --all-extras        # Setup Python env
scripts/get-database.py     # Fetch latest db

# Start the Django and Vue servers together
# Django http://localhost:8000/
# Vue http://localhost:5173/ (use this one)
npm run start
```

## Environment Variables
Secrets are loaded from .env in the repository root.

### Production Deploy
- Keep a .env file on the remote host at ~/pushingkarma/.env.
- fab deploy --full validates this file exists before building/restarting.
- Deploy rsync excludes `.env` so remote secrets are not overwritten or deleted.


## Other Useful Package Commands
```bash
npm run getdb          # Gets the Production sqlite db from http://pdash.nasuni.net/db.sqlite3
npm run start          # Starts Django and Vue servers together
npm run django         # Watch and reload Django when files changed
npm run vue            # Watch and reload Vue when files changed
npm run build          # Compile and Minify for Production
npm run eslint         # Lint with [ESLint](https://eslint.org/)
```

## Bash Access on Container
```
sudo docker exec -it pushingkarma /bin/bash
```

## References
* [Vue Extension for VSCode](https://marketplace.visualstudio.com/items?itemName=Vue.volar)
* [Vite Configuration Reference](https://vitejs.dev/config/)
* [Material Design Icons](https://pictogrammers.com/library/mdi/)
