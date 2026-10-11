#!/bin/sh
# One-time setup after cloning: turn on the leak-check hooks.
set -e
cd "$(dirname "$0")/.."
git config core.hooksPath .githooks
DENYLIST="${ROBO_DENYLIST:-$HOME/.config/robo-pizza-qiaowei/denylist.txt}"
if [ ! -f "$DENYLIST" ]; then
  echo "Hooks enabled, but no denylist at $DENYLIST - every commit will be refused until it exists."
  exit 0
fi
echo "Hooks enabled. Denylist: $DENYLIST"
