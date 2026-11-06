#!/bin/bash
set -euo pipefail
SSH="/c/Windows/System32/OpenSSH/ssh.exe"
"$SSH" -T -o BatchMode=yes spartan '
RUN=/data/gpfs/projects/punim2657/SfSpp/runs/20261106-0454_3695976_t311b-kladder-E
for a in BASER1 K6R1 K6R2 K2R2; do
  f=$RUN/work/logs/binary_E_${a}.log
  if [ -f "$f" ]; then
    echo "=== $(basename "$f") ==="
    tail -n 8 "$f"
  fi
done
'
