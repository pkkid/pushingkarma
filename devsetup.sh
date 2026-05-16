#!/usr/bin/env bash
# devsetup.sh
# Runs the dependency/bootstrap setup used by the VS Code "Install Dependencies"
# task. This script is designed to run from either the main repository checkout
# or a git worktree checkout, with separate branches for each case.
set -euo pipefail

MAIN_REPO='/home/pkkid/Projects/pushingkarma'
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

# Detect whether this checkout is a worktree.
is_worktree=false
if [[ "$(git rev-parse --git-common-dir 2>/dev/null || true)" != '.git' ]]; then
  is_worktree=true
fi

if [[ "$is_worktree" != 'true' ]]; then
  # Main-repo setup path.
  echo 'Running setup for main repo'
  npm install
  uv sync --all-extras
else
  # Worktree setup path.
  echo 'Running setup for worktree'
  npm install
  uv sync
  ln -sf "$MAIN_REPO/.env" .env
  cp -n "$MAIN_REPO/pk/db.sqlite3" pk/db.sqlite3
fi
