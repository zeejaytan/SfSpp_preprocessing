#!/bin/bash
set -euo pipefail
export MSYS_NO_PATHCONV=1 MSYS2_ARG_CONV_EXCL='*'
SSH="/c/Windows/System32/OpenSSH/ssh.exe"
"$SSH" -T -o BatchMode=yes -o ConnectTimeout=25 spartan "
scontrol show job 34427816 | grep -E 'JobState|Reason|StartTime|Priority|NumCPUs|MinMemory|TimeLimit'
squeue -p sapphire --states=PD --sort=-p -o '%.10i %.10Q %.9P %.12j %.8u %.2t %.10l %.6C %.10m %.20R %.20S' | head -20
"
