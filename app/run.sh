#!/bin/sh
set -x

SESSION="default"

if ! tmux has-session -t "$SESSION" 2>/dev/null; then
  tmux new-session -d -s "$SESSION"
fi

mega-cmd-server --do-not-log-to-stdout &

cd "$(dirname "$0")"
exec python3 main.py
