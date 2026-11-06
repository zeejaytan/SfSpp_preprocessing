#!/bin/bash
set -euo pipefail
SSH="/c/Windows/System32/OpenSSH/ssh.exe"
"$SSH" -T -o BatchMode=yes spartan '
RUN2=/data/gpfs/projects/punim2657/SfSpp/runs/20261106-0624_3695976_t311b2-kladder-K23
echo "=== K3R2 ==="
tail -n 8 $RUN2/work/logs/binary_E_K3R2.log
echo "=== K2R2 ==="
tail -n 8 $RUN2/work/logs/binary_E_K2R2.log
'
