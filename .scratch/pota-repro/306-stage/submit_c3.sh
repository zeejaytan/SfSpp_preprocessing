#!/bin/bash
# Ticket 306 Stage C3 submission: 163-piece corpus axis extraction with the union rule.
# Creates the run dir, copies the uncommitted sfs_axes working tree, submits, records the index row.
set -euo pipefail
SSH="/c/Windows/System32/OpenSSH/ssh.exe"
SCP="/c/Windows/System32/OpenSSH/scp.exe"
TICKET=C:/PR/worktrees/sfs/306
STAGE=$TICKET/.scratch/pota-repro/306-stage
RUNS=/data/gpfs/projects/punim2657/SfSpp/runs

TS=$("$SSH" spartan 'date -u +%Y%m%d-%H%M')
RUNID="${TS}_c333dc7_t306c-corpus-union"
RUN="$RUNS/$RUNID"
echo "RUNID=$RUNID"

"$SSH" spartan "mkdir -p $RUN/logs $RUN/work/code"

cd "$TICKET"
rm -rf sfs_axes/__pycache__
"$SCP" "$STAGE/submit306c.sbatch" "spartan:$RUN/submit.sbatch"
"$SCP" -r sfs_axes "spartan:$RUN/work/code/"
"$SCP" "$STAGE/idx_append.py" spartan:/tmp/idx_append.py

OUT=$("$SSH" spartan "cd $RUN && md5sum submit.sbatch && md5sum work/code/sfs_axes/*.py && sbatch submit.sbatch")
echo "$OUT"
JOB=$(echo "$OUT" | sed -n 's/^Submitted batch job \([0-9]*\)$/\1/p')
[ -n "$JOB" ] || { echo "no job id"; exit 1; }
echo "JOB=$JOB  RUN=$RUN"

"$SSH" spartan "python3 /tmp/idx_append.py $RUNID $JOB c333dc7 t306c-corpus-union"
