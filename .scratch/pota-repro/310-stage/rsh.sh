#!/usr/bin/env bash
# rsh.sh -- run one remote command on spartan with retries (login node resets kex).
export MSYS_NO_PATHCONV=1 MSYS2_ARG_CONV_EXCL='*'
SSH=/c/Windows/System32/OpenSSH/ssh.exe
CMD="$1"
for i in $(seq 1 10); do
  out=$("$SSH" -o ConnectTimeout=25 spartan "$CMD" 2>&1)
  rc=$?
  if [ $rc -eq 0 ]; then echo "$out"; exit 0; fi
  case "$out" in
    *"Connection reset"*|*"kex_exchange_identification"*|*"Connection closed"*|*"timed out"*) sleep 8;;
    *) echo "$out"; exit $rc;;
  esac
done
echo "RSH: gave up"; exit 1
