#!/bin/bash
# Ticket 310 stage C2: as each pot's rule axes land, submit that pot's seating job
# (our axes MM against the authors' axes MO, both arms in one allocation, 2 repeats
# each).  Pot order is small-first so the delta table fills while the big pots run.
set -uo pipefail
export MSYS_NO_PATHCONV=1 MSYS2_ARG_CONV_EXCL='*'
SSH="/c/Windows/System32/OpenSSH/ssh.exe"
AXP=/data/gpfs/projects/punim2657/SfSpp/runs/20261105-1215_1a6f16e_t310b3-timing/out/axes310
CORP=/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp
cd /c/PR/worktrees/sfs/310/.scratch/pota-repro/310-stage || exit 1

rssh() { local i; for i in $(seq 1 12); do "$SSH" -o ConnectTimeout=25 spartan "$1" && return 0; sleep 10; done; return 1; }

for p in A B C D E F G H I J; do
  if awk '{print $1}' /tmp/t310c2_jobs.txt 2>/dev/null | grep -qx "$p"; then
    echo "-- $p already in C2 record, skip"; continue
  fi
  need=$(rssh "ls $CORP/Surfaces/Pot_${p}_Piece_*_Surface_0.xyz 2>/dev/null | wc -l")
  for i in $(seq 1 240); do
    have=$(rssh "ls $AXP/Pot_${p}_Piece_*_Axis.xyz 2>/dev/null | wc -l")
    [ "${have:-0}" -ge "${need:-1}" ] && break
    sleep 60
  done
  echo "== $p axes $have / $need -> submit"
  JF=/tmp/t310c2_jobs.txt POTS="$p" ARMSPEC='MO:2 MM:2' TAG=t310c2 bash submit310e.sh 2>&1 | tail -8
done
echo "== C2 DONE"
cat /tmp/t310c2_jobs.txt 2>/dev/null
