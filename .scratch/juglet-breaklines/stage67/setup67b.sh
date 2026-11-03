#!/bin/bash
# setup67b.sh -- copy job-2 instruments at the pushed commit into the t67 run dir and submit submit67b.sbatch.
# Job-1 copies of changed instruments are kept as <name>.job1.
set -euo pipefail
BR=67-juglet-assembly-scaled-floor
CAN=/data/gpfs/projects/punim2657/sfs_preprocessing
P=.scratch/juglet-breaklines/stage67
RUN=/data/gpfs/projects/punim2657/SfSpp/runs/20261103-1429_3b3efbc_t67-juglet-assembly
git -C $CAN fetch -q origin $BR
C=$(git -C $CAN rev-parse FETCH_HEAD)
[ -f $RUN/instruments/arm67.sh.job1 ] || cp $RUN/instruments/arm67.sh $RUN/instruments/arm67.sh.job1
for f in patch_attitude67.py arm67.sh submit67b.sbatch; do
  git -C $CAN show $C:$P/$f > $RUN/instruments/$f
done
cp $RUN/instruments/submit67b.sbatch $RUN/submit_b.sbatch
echo "job2 commit $C" >> $RUN/instruments/COMMITS.txt
cd $RUN
J=$(sbatch --parsable submit_b.sbatch)
echo "COMMIT $C"
echo "JOB $J"
