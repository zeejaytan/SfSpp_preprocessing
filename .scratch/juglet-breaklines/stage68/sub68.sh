#!/bin/bash
# sub68.sh -- submit the prepared t68 Part A run and append its index row (verdict/note left empty).
set -euo pipefail
RUN=/data/gpfs/projects/punim2657/SfSpp/runs/20261103-1523_4b516be_t68-axis-method
cd $RUN
J=$(sbatch --parsable submit.sbatch)
sed -i 's/"submitted": false/"submitted": true, "jobid": "'"$J"'"/' run.json
printf '%s\t%s\t%s\t%s\t\t\n' "$(basename $RUN)" "$J" "4b516be" "t68-axis-method" >> /data/gpfs/projects/punim2657/SfSpp/runs/index.tsv
tail -1 /data/gpfs/projects/punim2657/SfSpp/runs/index.tsv
echo "JOB $J"
