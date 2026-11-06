#!/bin/bash
set -euo pipefail
export MSYS_NO_PATHCONV=1 MSYS2_ARG_CONV_EXCL='*'
SSH="/c/Windows/System32/OpenSSH/ssh.exe"
"$SSH" -T -o BatchMode=yes -o ConnectTimeout=25 spartan '
grep -rn "pragma" /data/gpfs/projects/punim2657/sfs_main/sfspreproc-docker/class/ /data/gpfs/projects/punim2657/sfs_main/sfspreproc-docker/hpc/ 2>/dev/null || true
'
