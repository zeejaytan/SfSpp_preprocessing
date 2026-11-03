#!/bin/bash
# setup68g.sh -- t68 guard proof-build: scratch dir guard68/ under the job-1 run dir; submit.
# Canonical checkouts: fetch / archive only.
set -euo pipefail
BR=68-axis-method-guard-densify
CAN=/data/gpfs/projects/punim2657/sfs_preprocessing
P=.scratch/juglet-breaklines/stage68
P67=.scratch/juglet-breaklines/stage67
RUN1=/data/gpfs/projects/punim2657/SfSpp/runs/20261103-1523_4b516be_t68-axis-method
T58=/data/gpfs/projects/punim2657/SfSpp/runs/20261101-1913_d8f716f_t58-floor-density-panel
git -C $CAN fetch -q origin $BR
C=$(git -C $CAN rev-parse FETCH_HEAD)
RUN=$RUN1/guard68
mkdir -p $RUN/logs $RUN/out $RUN/instruments/axes68
for f in stage67_inputs.py arm67.sh; do git -C $CAN show $C:$P67/$f > $RUN/instruments/$f; done
git -C $CAN show $C:$P/partB/guard68.patch > $RUN/instruments/guard68.patch
git -C $CAN show $C:$P/submit68g.sbatch > $RUN/submit.sbatch
cp $T58/work/juglet_orig_block.inc $RUN/instruments/
cp $RUN1/axes68/*.xyz $RUN/instruments/axes68/
md5sum $RUN/instruments/guard68.patch $RUN/instruments/juglet_orig_block.inc
cat > $RUN/run.json <<EOF
{
  "ticket": "68-axis-method-guard-densify",
  "part": "B guard proof-build",
  "commit": "$C",
  "assembler_commit": "cc1d859 (git archive copy; sfs_main/sfspreproc-docker untouched)",
  "tag": "t68-guard-proof",
  "arms": {"GJ50": "Juglet floor 50, t66 lanes + t68 axes", "GPA50": "Pot A floor 50"},
  "created": "$(date -u +%FT%TZ)"
}
EOF
cd $RUN
J=$(sbatch --parsable submit.sbatch)
printf '%s\t%s\t%s\t%s\t\t\n' "20261103-1523_4b516be_t68-axis-method/guard68" "$J" "${C:0:7}" "t68-guard-proof" >> /data/gpfs/projects/punim2657/SfSpp/runs/index.tsv
echo "RUN $RUN"; echo "JOB $J"
