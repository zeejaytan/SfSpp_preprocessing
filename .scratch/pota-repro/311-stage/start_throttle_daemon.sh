#!/bin/bash
set -euo pipefail
export MSYS_NO_PATHCONV=1 MSYS2_ARG_CONV_EXCL='*'
SSH="/c/Windows/System32/OpenSSH/ssh.exe"
SCP="/c/Windows/System32/OpenSSH/scp.exe"
RUN=/data/gpfs/projects/punim2657/SfSpp/runs/20261106-0454_3695976_t311b-kladder-E
"$SCP" -q -o BatchMode=yes C:/PR/worktrees/sfs/311/.scratch/pota-repro/311-stage/throttle311b.py "spartan:$RUN/work/throttle311b.py"
"$SSH" -T -o BatchMode=yes spartan "
if ! pgrep -f 'throttle311b.py --daemon' >/dev/null 2>&1; then
  nohup srun --jobid=34427816 --overlap /data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3 $RUN/work/throttle311b.py --daemon > $RUN/logs/throttle_daemon.log 2>&1 < /dev/null &
  sleep 3
fi
cat $RUN/logs/throttle_daemon.log 2>/dev/null || true
"
