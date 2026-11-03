#!/bin/bash
# setup68.sh -- run on the Spartan login node via rsh.ps1. Creates the t68 Part A run dir from the
# pushed commit and PREPARES submit.sbatch; it does NOT submit and writes no index.tsv row.
# Canonical checkout: fetch only, no checkout, no edit. Dataset/ is only read (md5s).
set -euo pipefail
BR=68-axis-method-guard-densify
CAN=/data/gpfs/projects/punim2657/sfs_preprocessing
P=.scratch/juglet-breaklines/stage68
P67=.scratch/juglet-breaklines/stage67
git -C $CAN fetch -q origin $BR
C=$(git -C $CAN rev-parse FETCH_HEAD)
C7=${C:0:7}
RUN=/data/gpfs/projects/punim2657/SfSpp/runs/$(date +%Y%m%d-%H%M)_${C7}_t68-axis-method
mkdir -p $RUN/logs $RUN/out $RUN/work $RUN/instruments $RUN/axes68
for f in patch_guard67.py stage67_inputs.py arm67.sh; do
  git -C $CAN show $C:$P67/$f > $RUN/instruments/$f
done
for f in submit68.sbatch hybrid68.py fit68.py; do
  git -C $CAN show $C:$P/$f > $RUN/instruments/$f
done
for k in 1 2 3 4 5 6 7 8 9; do
  git -C $CAN show $C:$P/axes_hybrid/Juglet_Piece_${k}_Axis.xyz > $RUN/axes68/Juglet_Piece_${k}_Axis.xyz
done
git -C $CAN show $C:$P/axes_hybrid/selection.tsv > $RUN/axes68/selection.tsv
cp $RUN/instruments/submit68.sbatch $RUN/submit.sbatch
{
  echo "--- t68 hybrid axes (substituted)"
  md5sum $RUN/axes68/*
  echo "--- old axes, the two Dataset trees (the t67 job staged from sfs_preprocessing/Dataset)"
  md5sum /data/gpfs/projects/punim2657/Dataset/Axes/Juglet/*.xyz
  md5sum /data/gpfs/projects/punim2657/sfs_preprocessing/Dataset/Axes/Juglet/*.xyz
  echo "--- GT, the two Dataset trees"
  md5sum /data/gpfs/projects/punim2657/Dataset/Juglet_GT/*.txt
  md5sum /data/gpfs/projects/punim2657/sfs_preprocessing/Dataset/Juglet_GT/*.txt 2>&1
} > $RUN/logs/axes_provenance.log
cat > $RUN/run.json <<EOF
{
  "ticket": "68-axis-method-guard-densify",
  "repo": "zeejaytan/SfSpp_preprocessing",
  "branch": "$BR",
  "commit": "$C",
  "tag": "t68-axis-method",
  "part": "A: Juglet axes re-estimated from each piece's own walls; F20 panel rerun with them substituted",
  "axes": "axes68/ (hybrid68.py: estimators see only t66 arm-U S0/S1 walls; the per-piece CHOICE between estimators was made by the GT gate; selection.tsv)",
  "arms": {"F20O": "floor 20, old Dataset axes (baseline, = t67 F20)", "F20N": "floor 20, axes68 substituted"},
  "lanes": "/data/gpfs/projects/punim2657/SfSpp/runs/20261103-1332_fab76f5_t66-admitsign-default/outU_jug/geom (read-only)",
  "panel_recipe": "t67 run 20261103-1429_3b3efbc_t67-juglet-assembly (read-only)",
  "submitted": false,
  "created": "$(date -u +%FT%TZ)"
}
EOF
echo "RUN $RUN"
echo "COMMIT $C"
cat $RUN/logs/axes_provenance.log
ls -la $RUN $RUN/axes68
