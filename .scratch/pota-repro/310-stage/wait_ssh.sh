#!/bin/bash
set -uo pipefail
export MSYS_NO_PATHCONV=1 MSYS2_ARG_CONV_EXCL='*'
SSH=/c/Windows/System32/OpenSSH/ssh.exe
for i in $(seq 1 20); do
  sleep 15
  out=$("$SSH" -o ConnectTimeout=20 spartan 'echo alive; squeue -u zhuojiat -h -o "%i %T"' 2>&1) && { echo "$out"; exit 0; }
  echo "try $i: $(echo "$out" | head -1)"
done
exit 1