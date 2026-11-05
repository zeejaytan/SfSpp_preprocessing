#!/bin/bash
# Ticket 306 Stage B1/B2/B3/B4 submission (retry). Creates the run dir, copies the
# uncommitted sfs_axes working tree and the stage scripts, submits, records the index row.
set -euo pipefail
SSH="/c/Windows/System32/OpenSSH/ssh.exe"
SCP="/c/Windows/System32/OpenSSH/scp.exe"
TICKET=C:/PR/worktrees/sfs/306
STAGE=$TICKET/.scratch/pota-repro/306-stage
RUNS=/data/gpfs/projects/punim2657/SfSpp/runs

TS=$("$SSH" spartan 'date -u +%Y%m%d-%H%M')
RUNID="${TS}_c333dc7_t306b1-union-a2"
RUN="$RUNS/$RUNID"
echo "RUNID=$RUNID"

"$SSH" spartan "mkdir -p $RUN/logs $RUN/work/code"

cd "$TICKET"
"$SCP" "$STAGE/submit306b.sbatch" "$STAGE/run_one_306b.sh" "$STAGE/analyse306b.py" "spartan:$RUN/work/"
"$SCP" "$STAGE/submit306b.sbatch" "spartan:$RUN/submit.sbatch"
"$SCP" -r sfs_axes "spartan:$RUN/work/code/"
"$SCP" "$STAGE/idx_append.py" spartan:/tmp/idx_append.py

OUT=$("$SSH" spartan "cd $RUN && md5sum submit.sbatch && sbatch --export=ALL,RUNID=$RUNID submit.sbatch")
echo "$OUT"
JOB=$(echo "$OUT" | sed -n 's/^Submitted batch job \([0-9]*\)$/\1/p')
[ -n "$JOB" ] || { echo "no job id"; exit 1; }
echo "JOB=$JOB  RUN=$RUN"

"$SSH" spartan "python3 /tmp/idx_append.py $RUNID $JOB c333dc7 t306b1-union-a2"
