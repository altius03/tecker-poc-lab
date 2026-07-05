#!/bin/zsh
set -euo pipefail

SCRIPT_DIR="${0:A:h}"

python3 "$SCRIPT_DIR/mac_agent.py" \
  --ps-file <(/bin/ps -axo pid=,ppid=,%cpu=,%mem=,comm=) \
  --lsof-file <(/usr/sbin/lsof -nP -iTCP -sTCP:ESTABLISHED -sTCP:LISTEN) \
  --sw-vers-file <(/usr/bin/sw_vers) \
  --uptime-file <(/usr/bin/uptime)
