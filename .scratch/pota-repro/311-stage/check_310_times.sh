#!/usr/bin/env bash
set -euo pipefail
SSH="/c/Windows/System32/OpenSSH/ssh.exe -T -o BatchMode=yes"
$SSH spartan '
R310=/data/gpfs/projects/punim2657/SfSpp/runs/20261105-1407_1a6f16e_t310c2-E
for f in $R310/work/logs/binary_*.log; do
  echo "=== $(basename $f) ==="
  grep -n "W110\|Expend\|Total time\|Sherd accuracy" "$f" | head -n 15
  echo "..."
  grep -n "W110\|Expend\|Total time\|Sherd accuracy" "$f" | tail -n 20
done
'
