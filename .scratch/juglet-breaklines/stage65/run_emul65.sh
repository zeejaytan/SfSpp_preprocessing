#!/bin/bash
# Ticket 65 stage 2c-falsify: emulate the admission side rule on the frozen t62F and t55 bundles,
# then score with the frozen scorer and the t65 side/stage-1 tables. Read-only on the inputs.
set -u
RU=/data/gpfs/projects/punim2657/SfSpp/runs
RD=$RU/20261103-0515_aee7ba0_t65-j1-localise
PY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3
W=$RD/work
E=$RD/out/emul
G62=$RU/20261103-0035_ca520fe_t62-normalfix-s2/outF
G55=$RU/20261101-2004_05be12c_t55-worness07-breaklines/out
mkdir -p $E
cd $W
$PY t65_emul.py $E emulF=$G62/geom=$G62/pieces emul55=$G55/geom=$G55/pieces || exit 1
for a in emulF emul55; do
  $PY $RU/20261102-0450_05be12c_t57-sweep/check_separation.py --geom $E/$a \
      --mesh-dir /data/gpfs/projects/punim2657/Dataset/Mesh/Juglet \
      --walls $RU/20261101-1613_83edd76_t54-worness-dial/out/wall40 \
      --out-tsv $E/sep_$a.tsv --quiet 2> $E/sep_$a.err
  echo "sep $a rc=$?"
done
$PY t65_sector.py $E/sector emulF=$E/emulF emul55=$E/emul55 > $E/sector.log 2>&1; echo "sector rc=$?"
$PY t65_stage1.py $E/stage1 emulF=$E/emulF emul55=$E/emul55 > $E/stage1.log 2>&1; echo "stage1 rc=$?"
echo done
