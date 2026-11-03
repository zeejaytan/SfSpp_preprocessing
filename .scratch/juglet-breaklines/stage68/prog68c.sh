#!/bin/bash
# read-only: progress of the edgeline cells in t68 job 2
RUN=/data/gpfs/projects/punim2657/SfSpp/runs/20261103-1535_ffcb350_t68-densify
date -u +%FT%TZ
for C in D190 D095; do
  echo "== $C"; grep -a -E "\[CELL66\] (piece|mesh rc|edge rc|breakline 0)" $RUN/logs/cell_$C.log 2>/dev/null | tail -4
done
