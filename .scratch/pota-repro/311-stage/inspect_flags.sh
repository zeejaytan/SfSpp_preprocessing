#!/usr/bin/env bash
set -euo pipefail
SSH="/c/Windows/System32/OpenSSH/ssh.exe -T -o BatchMode=yes"
$SSH spartan '
R311=/data/gpfs/projects/punim2657/SfSpp/runs/20261106-0454_3695976_t311b-kladder-E
cat $R311/work/logs/flags_E_MOR1.log
cat $R311/work/logs/link_E_MOR1.txt
sstat -j 34427816.batch --format=JobID,AveCPU,MinCPU,MaxRSS,NTasks 2>/dev/null || true
'
