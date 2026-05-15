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
npm run build               # Compiles Vue and runs Django collectstatic
uv run python pk/manage.py <cmd>    # Run Django management commands
uv run fab deploy           # Deploy to production server
uv run fab deploy --full    # Full deployment with Docker rebuild
```

## Architecture
### Backend (Django)
- Django apps structure: Each major feature is a separate Django app under `pk/apps/`
  - `main/`: Core website functionality and homepage
  - `budget/`: Financial transaction tracking and categorization
  - `stocks/`: Stock portfolio monitoring with yfinance integration
  - `obsidian/`: Integration with Obsidian vault for notes
- API Architecture: Uses Django Ninja for REST API with automatic OpenAPI docs
  - All APIs are mounted under `/api/` prefix
  - Each app has its own router (`api.py`) with schemas defined in `schemas.py`
  - Central API configuration in `pk/urls.py`
- Database: SQLite with Django ORM models
  - Transaction data with automatic categorization rules
  - Stock ticker history and portfolio tracking
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
  - Assets served from `public/static/`
  - Development proxy handles Vue dev server fallback

### Key Integrations
- Highlight.js: Code syntax highlighting for markdown content
- Chart.js: Financial charts and data visualization
- Markdown processing: Custom markdown renderer with callouts and TOC
- Obsidian vault: File-based notes integration with live sync

## Development Workflow
1. Database changes: Create migrations with `uv run python pk/manage.py makemigrations`
2. Static files: Auto-collected during build process, served from `_dist/static/`
3. API testing: Use `/apidoc` route for interactive API documentation
4. Logs: Development logs written to `_logs/` directory

## Production Deployment
- Docker: Containerized deployment with nginx + supervisord
- Fabric: Automated deployment scripts in `fabfile.py`
- Static hosting: Built Vue app served directly by nginx
- Database: SQLite file persisted via Docker volume mounts

## New Tab Page
The new tab page (`vue/views/newtab/`) is a browser new-tab replacement that
displays a dashboard of system stats widgets. Each widget is a standalone Vue
component under `vue/views/newtab/`.

### Glances Integration
All system stats widgets source their data from a [Glances](https://nicolargo.github.io/glances/)
instance running on the local network. The `useGlances` composable (`vue/composables/useGlances.js`)
is a singleton that polls the Glances

## Code Style
### Python
Functions should be simple and clean. After creating a new function, always ask
yourself "Can this be made simpler or cleaner in any way?" Don't use blank lines
within a function to seperate different sections of the work to perform, instead
fill the blank lines with comments.

### Javascript
Don't use end line semicolons. Always use open and close brackets for if statements,
even if the if statement is a single line. Only use the `() => <logic>` function
syntax if the function is a single line. If the function is mutliple lines long,
use the longer `function() { <logic> }` syntax.
