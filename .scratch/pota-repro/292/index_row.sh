#!/usr/bin/env bash
set -euo pipefail
IDX=/data/gpfs/projects/punim2657/SfSpp/runs/index.tsv
RUNID=20261025-0134_787c149_p292-rescore
JOBID=$1
COMMIT=787c149a3e5b8e4b23093746677b7842452e9316
TAG=p292-rescore
HEADER=$(head -1 $IDX)
EXPECTED=$(printf "runid\tjobid\tcommit\ttag\tverdict\thuman_note")
if [ "$HEADER" != "$EXPECTED" ]; then echo "[INDEX] header mismatch: $HEADER"; exit 2; fi
if grep -q "^$RUNID" $IDX; then echo "[INDEX] row already present for $RUNID"; exit 3; fi
printf "%s\t%s\t%s\t%s\t\t\n" "$RUNID" "$JOBID" "$COMMIT" "$TAG" >> $IDX
echo "[INDEX] appended:"; tail -1 $IDX | cat -A | head -2
echo "[INDEX] rows=$(wc -l < $IDX)"