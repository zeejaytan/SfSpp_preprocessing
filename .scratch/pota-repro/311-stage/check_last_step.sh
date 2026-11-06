#!/bin/bash
set -euo pipefail
SSH="/c/Windows/System32/OpenSSH/ssh.exe"
"$SSH" -T -o BatchMode=yes spartan '
RUN=/data/gpfs/projects/punim2657/SfSpp/runs/20261106-0454_3695976_t311b-kladder-E
grep -E "Start : [0-9]+ Step" $RUN/work/logs/binary_E_K1R1.log | tail -n 5
'
