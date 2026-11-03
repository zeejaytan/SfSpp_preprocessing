#!/bin/bash
# setup67.sh -- run on the Spartan login node via rsh.ps1. Creates the t67 run dir from a pushed commit
# and submits submit67.sbatch from it. Canonical checkout: fetch only, no checkout, no edit.
set -euo pipefail
BR=67-juglet-assembly-scaled-floor
CAN=/data/gpfs/projects/punim2657/sfs_preprocessing
P=.scratch/juglet-breaklines/stage67
git -C $CAN fetch -q origin $BR
C=$(git -C $CAN rev-parse FETCH_HEAD)
C7=${C:0:7}
RUN=/data/gpfs/projects/punim2657/SfSpp/runs/$(date +%Y%m%d-%H%M)_${C7}_t67-juglet-assembly
mkdir -p $RUN/logs $RUN/out $RUN/work $RUN/instruments
for f in patch_guard67.py stage67_inputs.py arm67.sh submit67.sbatch; do
  git -C $CAN show $C:$P/$f > $RUN/instruments/$f
done
cp $RUN/instruments/submit67.sbatch $RUN/submit.sbatch
cat > $RUN/run.json <<EOF
{
  "ticket": "67-juglet-assembly-scaled-floor",
  "repo": "zeejaytan/SfSpp_preprocessing",
  "branch": "$BR",
  "commit": "$C",
  "tag": "t67-juglet-assembly",
  "arms": {"F50G": 50, "F30": 30, "F20": 20, "SCL17": 17, "PACTL": "50 (Pot A control)"},
  "guard": "patch_guard67.py: shim-level early exit when the pruned LCS list is empty, and when out_state_ is empty",
  "lanes": "/data/gpfs/projects/punim2657/SfSpp/runs/20261103-1332_fab76f5_t66-admitsign-default/outU_jug/geom (read-only)",
  "staging_recipe": "t58 run 20261101-1913_d8f716f_t58-floor-density-panel (read-only)",
  "shim": "/data/gpfs/projects/punim2657/sfs_main/sfspreproc-docker/hpc/tools/main_pristine_batch.cpp (copied, never edited)",
  "created": "$(date -u +%FT%TZ)"
}
EOF
cd $RUN
J=$(sbatch --parsable submit.sbatch)
echo "RUN $RUN"
echo "COMMIT $C"
echo "JOB $J"
printf '%s\t%s\t%s\t%s\t\t\n' "$(basename $RUN)" "$J" "$C7" "t67-juglet-assembly" >> /data/gpfs/projects/punim2657/SfSpp/runs/index.tsv
tail -1 /data/gpfs/projects/punim2657/SfSpp/runs/index.tsv
