#!/bin/bash
set -euo pipefail
export MSYS_NO_PATHCONV=1 MSYS2_ARG_CONV_EXCL='*'
SSH="/c/Windows/System32/OpenSSH/ssh.exe"
"$SSH" -T -o BatchMode=yes -o ConnectTimeout=25 spartan '
echo "=== 310c2-E panel.tsv ==="
cat /data/gpfs/projects/punim2657/SfSpp/runs/20261105-1407_1a6f16e_t310c2-E/logs/panel.tsv
echo "=== 308b-E panel.tsv and acc.tsv ==="
cat /data/gpfs/projects/punim2657/SfSpp/runs/20261105-0550_d330469_t308b-E/logs/panel.tsv
cat /data/gpfs/projects/punim2657/SfSpp/runs/20261105-0550_d330469_t308b-E/score/acc.tsv
'
