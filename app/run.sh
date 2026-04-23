#!/bin/sh
set -x

mega-cmd-server --do-not-log-to-stdout &

cd "$(dirname "$0")"
exec python3 main.py
