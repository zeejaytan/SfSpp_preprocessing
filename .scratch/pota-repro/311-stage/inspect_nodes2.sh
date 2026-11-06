#!/bin/bash
set -euo pipefail
export MSYS_NO_PATHCONV=1 MSYS2_ARG_CONV_EXCL='*'
SSH="/c/Windows/System32/OpenSSH/ssh.exe"
"$SSH" -T -o BatchMode=yes -o ConnectTimeout=25 spartan '
sinfo -p sapphire -N -o "%N %T %C %m %e" | tail -n +36
echo "=== other partitions ==="
sinfo -o "%P %a %l %D %T %c %m" | grep -E "idle|mixed"
'
