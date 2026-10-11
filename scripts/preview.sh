#!/bin/sh
# Build the site and serve it at http://127.0.0.1:8765 (Ctrl-C to stop).
# Re-run after editing anything in site/ or replays/.
set -e
cd "$(dirname "$0")/.."
python3 scripts/build_site.py
exec python3 -m http.server 8765 --bind 127.0.0.1 --directory dist
