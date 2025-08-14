# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

PushingKarma is a personal website and application suite built with Django REST backend and Vue.js frontend. The project includes a budget tracking system, stock portfolio monitoring, Obsidian notes integration, and personal website content.

## Development Commands

```bash
# Start both Django and Vue development servers (recommended)
npm run start

# Start individual servers
npm run django          # Django server on http://localhost:8000/
npm run vue             # Vue dev server on http://localhost:5173/ (use this URL)

# Build for production
npm run build           # Compiles Vue and runs Django collectstatic

# Python package management
uv run python pk/manage.py <command>  # Run Django management commands
uv lock                              # Update Python dependencies

# Deployment
uv run fab deploy                    # Deploy to production server
uv run fab deploy --full             # Full deployment with Docker rebuild
```

## Architecture

### Backend (Django)
- **Django apps structure**: Each major feature is a separate Django app under `pk/apps/`
  - `main/`: Core website functionality and homepage
  - `budget/`: Financial transaction tracking and categorization
  - `stocks/`: Stock portfolio monitoring with yfinance integration
  - `obsidian/`: Integration with Obsidian vault for notes

- **API Architecture**: Uses Django Ninja for REST API with automatic OpenAPI docs
  - All APIs are mounted under `/api/` prefix
  - Each app has its own router (`api.py`) with schemas defined in `schemas.py`
  - Central API configuration in `pk/urls.py`

- **Database**: SQLite with Django ORM models
  - Transaction data with automatic categorization rules
  - Stock ticker history and portfolio tracking
  - Custom `TimeStampedModel` base class for audit fields

### Frontend (Vue.js)
- **Single Page Application**: Vue 3 with Vue Router
- **File structure**: All Vue components in `vue/` directory
  - `components/`: Reusable UI components (DataTable, Gallery, Markdown, etc.)
  - `views/`: Page-level components for each app section
  - `composables/`: Vue composition API utilities
  - `utils/`: JavaScript utilities and API client

- **Build system**: Vite with custom configuration
  - Builds to `_dist/` directory
  - Assets served from `public/static/`
  - Development proxy handles Vue dev server fallback

### Key Integrations
- **Highlight.js**: Code syntax highlighting for markdown content
- **Chart.js**: Financial charts and data visualization
- **Markdown processing**: Custom markdown renderer with callouts and TOC
- **Obsidian vault**: File-based notes integration with live sync

## Development Workflow

1. **Database changes**: Create migrations with `uv run python pk/manage.py makemigrations`
2. **Static files**: Auto-collected during build process, served from `_dist/static/`
3. **API testing**: Use `/apidoc` route for interactive API documentation
4. **Logs**: Development logs written to `_logs/` directory

## Production Deployment

- **Docker**: Containerized deployment with nginx + supervisord
- **Fabric**: Automated deployment scripts in `fabfile.py`
- **Static hosting**: Built Vue app served directly by nginx
- **Database**: SQLite file persisted via Docker volume mounts

## Data Management Commands

The budget app includes several management commands for transaction processing:
- `categorize_trxs`: Auto-categorize transactions based on rules
- `clean_payees`: Normalize payee names for better categorization
- `dedupe_trxs`: Remove duplicate transactions
- `import_trxs`: Import transactions from OFX files

Stock data updates via `update_stocks` command that fetches from yfinance API.