#!/bin/bash
R=/data/gpfs/projects/punim2657/SfSpp/runs
for d in $R/20261105-0615_9c5eec2_t305-e2e-a-moom $R/20261105-0617_9c5eec2_t305-e2e-a-moom; do
  echo "== $d"
  cat $d/run.json 2>/dev/null
  echo "-- acc"; cat $d/score/acc.tsv 2>/dev/null
done
