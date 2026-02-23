#!/bin/bash
set -e

LOG_DIR="/var/log/ameno-bot"
LOG_FILE="$LOG_DIR/sync.log"

mkdir -p "$LOG_DIR"
exec >> "$LOG_FILE" 2>&1

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting sync"

cd "$(dirname "$0")"

# Pull latest code first so the subsequent push is never rejected
git pull

# Commit and push favorites.db only if it has changed
if ! git diff --quiet favorites.db; then
    git add favorites.db
    git commit -m "chore: update favorites.db $(date '+%Y-%m-%d %H:%M:%S')"
    git push
fi

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Sync complete"
