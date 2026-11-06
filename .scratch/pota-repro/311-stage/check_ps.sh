#!/usr/bin/env bash
set -euo pipefail
SSH="/c/Windows/System32/OpenSSH/ssh.exe -T -o BatchMode=yes"
$SSH spartan '
srun --jobid=34427816 --overlap ps -eo pid,pcpu,pmem,stat,etime,comm,args | grep -E "Hierarchy|apptainer|PID" || true
'
