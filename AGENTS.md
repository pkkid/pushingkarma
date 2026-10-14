## Project Overview
PushingKarma is a personal website and application suite. The project includes a
budget tracking system, stock portfolio monitoring, Obsidian notes integration,
and personal website content. The backend is using Django with Django Ninja to
provide API endpoints for the frontend. The frontend is using Vue with a home-grown
component library. Icons are from the materialdesignicons font.

## Development Commands
```bash
npm run start               # Start both Django and Vue development servers (recommended)
npm run django              # Start the Django dev server on http://localhost:8000/
npm run vue                 # Start the Vue dev server on http://localhost:5173/ (use this URL)
npm run build               # Build highlight.js themes and compile Vue to _dist/
uv run python pk/manage.py <cmd>    # Run Django management commands
uv run fab deploy           # Build, rsync to production, restart daphne and nginx
uv run fab deploy --full    # Also upload .env.production, rebuild Docker image, run migrations
nvm install && npm install  # Setup JS env (Node version pinned in .nvmrc)
uv sync --all-extras        # Setup Python env (includes ruff, fabric, ipython)
scripts/get-database.py     # Fetch today's db backup from Synology to pk/db.sqlite3 (--list, --date)
npx eslint vue              # Lint Vue/JS (config in eslint.config.js)
uv run ruff check pk        # Lint Python (config in pyproject.toml, line-length 125)
```
- There is no automated test suite. Verify changes by running the app (`npm run start`)
  and using the Vue dev server at http://localhost:5173/.
- The README mentions `npm run getdb` and `npm run eslint`, but those scripts do not exist
  in package.json; use the commands above instead.
- `npm run vue` and `npm run build` first run `scripts/build-hljsthemes.py` to generate
  highlight.js theme CSS.
- Settings are read from `.env` in the repo root (see `.env.example`). `DEBUG=true`
  switches cookies to non-secure/Lax, enables permissive CORS, and points Obsidian
  buckets at `~/Sync/Notes` instead of `/notes`.

## Architecture
### Backend (Django)
- Django apps structure: Each major feature is a separate Django app under `pk/apps/`
  - `main/`: Core website functionality and homepage
  - `budget/`: Financial transaction tracking and categorization
  - `stocks/`: Stock portfolio monitoring with yfinance integration
  - `obsidian/`: Integration with Obsidian vault for notes
  - `reddit/`: Reddit news feed via PRAW (API only, no models)
- API Architecture: Uses Django Ninja for REST API with automatic OpenAPI docs
  - All APIs are mounted under `/api/` prefix
  - Each app has its own router (`api.py`) with schemas defined in `schemas.py`
  - Central API configuration in `pk/urls.py`
- Database: SQLite with Django ORM models
  - Transaction data with automatic categorization rules
  - Stock tickers and their price history
  - Custom `TimeStampedModel` base class for audit fields

### Frontend (Vue.js)
- Single Page Application: Vue 3 with Vue Router
- File structure: All Vue components in `vue/` directory
  - `components/`: Reusable UI components (DataTable, Gallery, Markdown, etc.)
  - `views/`: Page-level components for each app section
  - `composables/`: Vue composition API utilities
  - `utils/`: JavaScript utilities and API client
- Build system: Vite with custom configuration
  - Builds to `_dist/` directory
  - Static assets live in `public/static/` and are copied into `_dist/static/`
  - No Vite proxy; Django redirects page requests to the Vite dev server (see below)

### Key Integrations
- Highlight.js: Code syntax highlighting for markdown content
- Chart.js: Financial charts and data visualization
- Markdown processing: Custom markdown renderer with callouts and TOC
- Obsidian vault: Notes are read directly from markdown files on disk (`OBSIDIAN_BUCKETS` in settings)

### How Frontend and Backend Connect
- In development, Django's catch-all `index` view (`pk/urls.py`) redirects to the Vite
  server on :5173 when it detects it running; in production it serves `_dist/index.html`.
- `vue/utils/api.js` is the single hand-maintained API client. Axios `baseURL` points to
  `:8000` in development and the same origin in production, sending the CSRF cookie as
  `X-CSRFToken`. When adding or renaming a Django Ninja endpoint, add the matching method
  to the corresponding object (`Main`, `Budget`, `Obsidian`, `Reddit`, `Stocks`) here.
- `vue/App.vue` loads `/api/main/global_vars` (built from `settings.GLOBALVARS` plus the
  current user) on startup and exposes shared state with `provide()`: `globalvars`,
  `user`/`setUser`, `notify`, and `axiosSettings`. Views read these with `inject()`.
- The `newtab` route renders without the site Navigation/Footer chrome.
- `@` is aliased to `vue/`. Components, composables and views are re-exported through
  `index.js` barrel files (e.g. `import {DataTable} from '@/components'`); add new ones
  to the relevant barrel.

### Backend Conventions
- Each app's router is mounted in `pk/urls.py` under `/api/<app>`. Routers that require
  login are created with `Router(auth=django_auth)`, and querysets are scoped to
  `request.user`.
- The `reddit` app has no models, so it is mounted as a router but is not listed in
  `INSTALLED_APPS`. Apps with models (or management commands) must be added there.
- Shared API helpers are in `pk/utils/ninja.py`: `PageSchema()` builds paginated response
  schemas, `paginate()` does page-number pagination, and `paginate_cursor()` does keyset
  pagination for large tables like budget transactions.
- List endpoints support a search query syntax via `django_searchquery`; search fields
  are declared as `*SEARCHFIELDS` lists at the top of each `api.py`.
- Errors are returned as JSON `{status, message}` by the exception handlers in `pk/urls.py`;
  raise `ninja.errors.HttpError` for expected failures.
- `pk/utils/django.py` holds `cache_response` (DB-backed view caching) and
  `QueryCounterMiddleware`, which logs or returns SQL query counts when a request sends
  the `Count-Queries: true` or `Log-Queries: true` header.
- Budget-specific tuning (payee scrubbing tokens, recurring-detection skip categories) lives
  in `BUDGET_*` settings in `pk/settings.py`. Budget import and categorization logic is in
  `pk/apps/budget/trxmanager.py` and `recurring.py`, and there are matching management commands.

## Development Workflow
1. Database changes: Create migrations with `uv run python pk/manage.py makemigrations`
2. Static files: Vite builds them into `_dist/static/`, which nginx serves at `/static/` in production
3. API testing: Use `/apidoc` route for interactive API documentation
4. Logs: Development logs written to `_logs/` directory

## Production Deployment
- Docker: Containerized deployment with nginx, daphne (ASGI) and cron run by supervisord
- Fabric: Automated deployment scripts in `fabfile.py`; requires local `.env` and `.env.production`
- Migrations only run on `fab deploy --full`; a plain deploy does not migrate
- Static hosting: nginx serves `/static/` from `_dist/static/` and proxies everything else
  to daphne; Django returns `_dist/index.html` for all non-API routes
- Database: SQLite file persisted via Docker volume mounts (the project dir is mounted at `/app`,
  the Obsidian notes read-only at `/notes`); deploy rsync skips `*.sqlite3` and `.env` files

## New Tab Page
The new tab page (`vue/views/newtab/`) is a browser new-tab replacement that
displays a dashboard of system stats widgets. Each widget is a standalone Vue
component under `vue/views/newtab/`.

### Glances Integration
All system stats widgets source their data from a [Glances](https://nicolargo.github.io/glances/)
instance running on the local network. The `useGlances` composable (`vue/composables/useGlances.js`)
is a singleton that polls Glances every 2 seconds while any widget is mounted. Widgets do not
call Glances directly: `useGlances` hits `/api/main/glances`, which proxies `/api/4/all` server-side
to avoid browser Private Network Access restrictions. The Glances host comes from an optional
`GLANCES_URL` setting, which is not defined in `pk/settings.py`, so the hard-coded default in
`pk/apps/main/api.py` is used.

## Code Style
### Python
Functions should be simple and clean. After creating a new function, always ask
yourself "Can this be made simpler or cleaner in any way?" Don't use blank lines
within a function to separate different sections of the work to perform, instead
fill the blank lines with comments.

### Javascript
Don't use end line semicolons. Always use open and close brackets for if statements,
even if the if statement is a single line. Only use the `() => <logic>` function
syntax if the function is a single line. If the function is multiple lines long,
use the longer `function() { <logic> }` syntax.
