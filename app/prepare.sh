#!/bin/sh
set -x

cd "$(dirname "$0")"

if [ ! -f "$CONFIG_HOME/machine-id" ]; then
    uuidgen >"$CONFIG_HOME/machine-id"
fi

if [ ! -e "/etc/machine-id" ]; then
    ln -s "$CONFIG_HOME/machine-id" "/etc/machine-id"
fi
