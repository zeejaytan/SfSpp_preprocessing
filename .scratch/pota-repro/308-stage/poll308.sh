#!/bin/bash
# background poll for ticket 308 stage B/C progress -> /tmp/poll308.log
SSH=/c/Windows/System32/OpenSSH/ssh.exe
LOG=/tmp/poll308.log
: > $LOG
for i in $(seq 1 200); do
  TS=$(date +%H:%M:%S)
  OUT=""
  for try in 1 2 3 4; do
    OUT=$($SSH -o ConnectTimeout=25 spartan 'for P in A D E I J; do D=$(ls -d /data/gpfs/projects/punim2657/SfSpp/runs/*t308b-$P 2>/dev/null | tail -1); printf "%-2s " $P; tail -n +2 $D/logs/panel.tsv 2>/dev/null | awk -F"\t" "{printf \"%s(%ss) \", \$1, \$7}"; echo; done; sacct -j 34376624,34376687,34376734,34376767,34376769 --format=JobID%12,State,Elapsed 2>/dev/null | grep -v "\.ba\|\.ex"' 2>/dev/null)
    [ -n "$OUT" ] && break
    sleep 15
  done
  { echo "=== $TS"; echo "$OUT"; } >> $LOG
  sleep 240
done
