#!/bin/bash
set -euo pipefail
SSH="/c/Windows/System32/OpenSSH/ssh.exe"
"$SSH" -T -o BatchMode=yes spartan '
RUN2=/data/gpfs/projects/punim2657/SfSpp/runs/20261106-0624_3695976_t311b2-kladder-K23
for f in $RUN2/work/logs/binary_E_*.log; do
  echo "=== $(basename "$f") ==="
  grep -E "Start : [0-9]+ Step|Sherd accuracy|Edge accuracy" "$f" | tail -n 5
done
'
