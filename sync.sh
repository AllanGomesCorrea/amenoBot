#!/bin/bash
set -e

cd "$(dirname "$0")"

# Pull latest code first so the subsequent push is never rejected
git pull

# Commit and push favorites.db only if it has changed
if ! git diff --quiet favorites.db; then
    git add favorites.db
    git commit -m "chore: update favorites.db $(date '+%Y-%m-%d')"
    git push
fi
