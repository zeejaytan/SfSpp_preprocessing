#!/bin/bash
# setup68d.sh -- create the t68 job-3 run dir (true 2x densify arm D2X) from the pushed commit and submit it.
# Canonical checkout: fetch only.
set -euo pipefail
BR=68-axis-method-guard-densify
CAN=/data/gpfs/projects/punim2657/sfs_preprocessing
P=.scratch/juglet-breaklines/stage68
P67=.scratch/juglet-breaklines/stage67
git -C $CAN fetch -q origin $BR
C=$(git -C $CAN rev-parse FETCH_HEAD)
C7=${C:0:7}
RUN=/data/gpfs/projects/punim2657/SfSpp/runs/$(date +%Y%m%d-%H%M)_${C7}_t68-densify2x
mkdir -p $RUN/logs $RUN/out $RUN/work $RUN/instruments $RUN/axes68
for f in patch_guard67.py patch_attitude67.py stage67_inputs.py arm67.sh; do
  git -C $CAN show $C:$P67/$f > $RUN/instruments/$f
done
git -C $CAN show $C:$P/submit68d.sbatch > $RUN/instruments/submit68d.sbatch
for k in 1 2 3 4 5 6 7 8 9; do
  git -C $CAN show $C:$P/axes_hybrid/Juglet_Piece_${k}_Axis.xyz > $RUN/axes68/Juglet_Piece_${k}_Axis.xyz
done
cp $RUN/instruments/submit68d.sbatch $RUN/submit.sbatch
cat > $RUN/run.json <<EOF
{
  "ticket": "68-axis-method-guard-densify",
  "repo": "zeejaytan/SfSpp_preprocessing",
  "branch": "$BR",
  "commit": "$C",
  "tag": "t68-densify2x",
  "arms": {"D2X": "edgeline cell, t66 recipe, RESAMPLE_D_MM 0.95 AND sphereRadius 0.9 (edgeline_extraction_headless.cpp:556, :477)",
           "I20_D2X": "instrumented F20 panel on D2X lanes, axes68"},
  "why": "job 2 (20261103-1535_ffcb350_t68-densify) showed RESAMPLE_D_MM alone moves the exported Bl0 by +2-3 dots: the export is re-walked by the 1.8 mm sphere walk at :477",
  "mesh_stage_axes": "Dataset/Axes/Juglet (old, exactly as t66)",
  "created": "$(date -u +%FT%TZ)"
}
EOF
cd $RUN
J=$(sbatch --parsable --export=ALL,NEW=$C submit.sbatch)
printf '%s\t%s\t%s\t%s\t\t\n' "$(basename $RUN)" "$J" "$C7" "t68-densify2x" >> /data/gpfs/projects/punim2657/SfSpp/runs/index.tsv
echo "RUN $RUN"
echo "COMMIT $C"
echo "JOB $J"
