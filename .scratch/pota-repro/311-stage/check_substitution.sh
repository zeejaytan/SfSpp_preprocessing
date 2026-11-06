#!/bin/bash
set -euo pipefail
SSH="/c/Windows/System32/OpenSSH/ssh.exe"
"$SSH" -T -o BatchMode=yes spartan '
echo "=== 34427816 substitution.tsv ==="
cat /data/gpfs/projects/punim2657/SfSpp/runs/20261106-0454_3695976_t311b-kladder-E/logs/substitution.tsv
echo "=== 34431689 substitution.tsv ==="
cat /data/gpfs/projects/punim2657/SfSpp/runs/20261106-0624_3695976_t311b2-kladder-K23/logs/substitution.tsv
'
