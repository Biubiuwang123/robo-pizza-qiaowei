#!/bin/sh
# Convenience wrapper: scan the whole working tree.
cd "$(dirname "$0")/.." && exec python3 scripts/leak_check.py --all "$@"
