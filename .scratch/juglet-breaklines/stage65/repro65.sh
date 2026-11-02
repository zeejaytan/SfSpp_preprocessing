#!/bin/bash
# Ticket 65 stage 0a: re-run the frozen t62 frontier tables and the frozen scorer, diff against the frozen TSVs.
set -u
RUNS=/data/gpfs/projects/punim2657/SfSpp/runs
RD=$RUNS/20261103-0515_aee7ba0_t65-j1-localise
FR=$RUNS/20261103-0035_ca520fe_t62-normalfix-s2/work/lead-fast/frontier
PY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3
OUT=$RD/out/repro
mkdir -p $OUT
cd $OUT
$PY $FR/t62_labedge.py  > label_edge.tsv 2> label_edge.err
$PY $FR/t62_rev.py      > reverse.tsv    2> reverse.err
$PY $FR/t62_frontier.py > union_edge.tsv 2> union_edge.err
$PY $RUNS/20261102-0450_05be12c_t57-sweep/check_separation.py \
    --geom $RUNS/20261103-0035_ca520fe_t62-normalfix-s2/outF/geom \
    --mesh-dir /data/gpfs/projects/punim2657/Dataset/Mesh/Juglet \
    --walls $RUNS/20261101-1613_83edd76_t54-worness-dial/out/wall40 \
    --out-tsv sepF.tsv --quiet 2> sepF.err
$PY $RUNS/20261102-0450_05be12c_t57-sweep/check_separation.py \
    --geom $RUNS/20261101-2004_05be12c_t55-worness07-breaklines/out/geom \
    --mesh-dir /data/gpfs/projects/punim2657/Dataset/Mesh/Juglet \
    --walls $RUNS/20261101-1613_83edd76_t54-worness-dial/out/wall40 \
    --out-tsv sep55.tsv --quiet 2> sep55.err
for t in label_edge reverse union_edge; do
  if cmp -s $t.tsv $FR/$t.tsv; then echo "$t IDENTICAL"; else echo "$t DIFFERS"; diff $t.tsv $FR/$t.tsv | head -20; fi
done
if cmp -s sepF.tsv $RUNS/20261103-0035_ca520fe_t62-normalfix-s2/outF/sep.tsv; then echo "sepF IDENTICAL"; else echo "sepF DIFFERS"; diff sepF.tsv $RUNS/20261103-0035_ca520fe_t62-normalfix-s2/outF/sep.tsv | head; fi
echo done
