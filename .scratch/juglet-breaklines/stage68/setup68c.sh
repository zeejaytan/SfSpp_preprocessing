#!/bin/bash
# setup68c.sh -- create the t68 job-2 run dir (per-pair instrument + densify arm) from the pushed commit
# and submit it. Canonical checkout: fetch only.
set -euo pipefail
BR=68-axis-method-guard-densify
CAN=/data/gpfs/projects/punim2657/sfs_preprocessing
P=.scratch/juglet-breaklines/stage68
P67=.scratch/juglet-breaklines/stage67
git -C $CAN fetch -q origin $BR
C=$(git -C $CAN rev-parse FETCH_HEAD)
C7=${C:0:7}
RUN=/data/gpfs/projects/punim2657/SfSpp/runs/$(date +%Y%m%d-%H%M)_${C7}_t68-densify
mkdir -p $RUN/logs $RUN/out $RUN/work $RUN/instruments $RUN/axes68
for f in patch_guard67.py patch_attitude67.py stage67_inputs.py arm67.sh; do
  git -C $CAN show $C:$P67/$f > $RUN/instruments/$f
done
git -C $CAN show $C:$P/submit68c.sbatch > $RUN/instruments/submit68c.sbatch
for k in 1 2 3 4 5 6 7 8 9; do
  git -C $CAN show $C:$P/axes_hybrid/Juglet_Piece_${k}_Axis.xyz > $RUN/axes68/Juglet_Piece_${k}_Axis.xyz
done
cp $RUN/instruments/submit68c.sbatch $RUN/submit.sbatch
cat > $RUN/run.json <<EOF
{
  "ticket": "68-axis-method-guard-densify",
  "repo": "zeejaytan/SfSpp_preprocessing",
  "branch": "$BR",
  "commit": "$C",
  "tag": "t68-densify",
  "arms": {"I20N": "attitude instrument, floor 20, t66 lanes, axes68 (= F20N inputs)",
           "D190": "edgeline cell, t66 recipe, RESAMPLE_D_MM 1.9 (run-to-run control)",
           "D095": "edgeline cell, t66 recipe, RESAMPLE_D_MM 0.95 (2x density)",
           "I20_D190": "instrumented F20 panel on D190 lanes, axes68",
           "I20_D095": "instrumented F20 panel on D095 lanes, axes68"},
  "mesh_stage_axes": "Dataset/Axes/Juglet (old, exactly as t66) -- only the edge resample spacing differs between D190 and D095",
  "prior_run": "20261103-1523_4b516be_t68-axis-method (F20O/F20N)",
  "created": "$(date -u +%FT%TZ)"
}
EOF
cd $RUN
J=$(sbatch --parsable --export=ALL,NEW=$C submit.sbatch)
printf '%s\t%s\t%s\t%s\t\t\n' "$(basename $RUN)" "$J" "$C7" "t68-densify" >> /data/gpfs/projects/punim2657/SfSpp/runs/index.tsv
echo "RUN $RUN"
echo "COMMIT $C"
echo "JOB $J"
