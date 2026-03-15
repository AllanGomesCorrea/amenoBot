#!/bin/bash
set -e

LOG_DIR="/var/log/ameno-bot"
LOG_FILE="$LOG_DIR/sync.log"

mkdir -p "$LOG_DIR"
exec >> "$LOG_FILE" 2>&1

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting sync"

cd "$(dirname "$0")"

# Pull latest code first so the subsequent push is never rejected
BEFORE=$(git rev-parse HEAD)
git pull
AFTER=$(git rev-parse HEAD)

# Restart docker compose if remote had new changes
if [ "$BEFORE" != "$AFTER" ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Remote changes detected, restarting docker compose"
    docker compose down
    docker compose build
    docker compose up -d
fi

# Commit and push favorites.db only if it has changed
if ! git diff --quiet favorites.db; then
    git add favorites.db
    git commit -m "chore: update favorites.db $(date '+%Y-%m-%d %H:%M:%S')"
    git push
fi

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Sync complete"
