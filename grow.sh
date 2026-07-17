#!/bin/bash
# One night on the mesh: grow new nodes, commit, push (if a remote exists).
set -e
cd "$(dirname "$0")"

COUNT="${1:-4}"

EXTRA=""
if [ $((RANDOM % 3)) -eq 0 ]; then EXTRA="--renovate"; fi

python3 engine/grow.py --count "$COUNT" $EXTRA

# photograph a square from each node grown tonight (for the daily feed)
if [ -s logs/last-grown.txt ] && [ -d /opt/homebrew/lib/node_modules/playwright ]; then
  mkdir -p snapshots
  python3 -m http.server 8999 >/dev/null 2>&1 &
  SRV=$!
  sleep 1
  NODE_PATH=/opt/homebrew/lib/node_modules node engine/snap.cjs 8999 snapshots \
    $(cat logs/last-grown.txt) || echo "(snapshots failed, continuing)"
  kill $SRV 2>/dev/null || true
  python3 engine/caption.py >/dev/null 2>&1 || true
fi

git add -A
NIGHT=$(python3 -c "import json;print(json.load(open('rooms/manifest.json'))['nights'])")
git commit -m "night $NIGHT: the mesh grew" || exit 0

if git remote get-url origin >/dev/null 2>&1; then
  git pull --rebase && git push
fi
