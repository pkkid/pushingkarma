#!/usr/bin/env bash
# dev-setup.sh
# Runs the dependency/bootstrap setup used by the VS Code "Install Dependencies"
# task. This script is designed to run from either the main repository checkout
# or a git worktree checkout, with separate branches for each case.
set -euo pipefail
MAIN_REPO='/home/pkkid/Projects/pushingkarma'
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"
is_worktree=$([[ "$(git rev-parse --git-common-dir 2>/dev/null)" != '.git' ]] && echo '1' || true)

# Main Repo Setup
# Setup the main repo with all dependancies
if [[ -z "$is_worktree" ]]; then
  # Main-repo setup path.
  echo 'Running setup for main repo'
  npm install
  uv sync --all-extras
fi

# Worktree Setup
# Setup worktree with dependancies
if [[ -n "$is_worktree" ]]; then
  echo 'Running setup for worktree'
  npm install
  uv sync
  ln -sf "$MAIN_REPO/.env" .env
  cp -n "$MAIN_REPO/pk/db.sqlite3" pk/db.sqlite3
fi
