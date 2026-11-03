#!/bin/bash
# read-only: what the resample step did on piece 5 in both cells
RUN=/data/gpfs/projects/punim2657/SfSpp/runs/20261103-1535_ffcb350_t68-densify
for C in D190 D095; do
  echo "===== $C"
  grep -a -n -i -E "resampl|traced|length|equidist|segments|points" $RUN/outD${C#D}/pieces/Juglet_Piece_5/edge.log 2>/dev/null | head -30
done
