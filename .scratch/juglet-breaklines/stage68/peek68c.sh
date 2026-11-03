#!/bin/bash
# read-only: where is t68 job 2 now
RUN=/data/gpfs/projects/punim2657/SfSpp/runs/20261103-1535_ffcb350_t68-densify
date -u +%FT%TZ
ls -la --time-style=+%H:%M:%S $RUN $RUN/logs | tail -30
for f in $RUN/logs/build_*.log $RUN/logs/cell_*.log; do [ -f $f ] && { echo "== $f"; tail -4 $f; }; done
