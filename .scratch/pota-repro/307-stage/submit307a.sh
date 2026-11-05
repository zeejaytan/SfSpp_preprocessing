#!/bin/bash
# Ticket 307 Stage B: the axis sets (Pot A arms x seeds, corpus in two settings).
# Creates the run dir, copies the uncommitted sfs_axes working tree, submits, records the index row.
set -euo pipefail
SSH="/c/Windows/System32/OpenSSH/ssh.exe"
SCP="/c/Windows/System32/OpenSSH/scp.exe"
TICKET=C:/PR/SfSpp_preprocessing
STAGE=$TICKET/.scratch/pota-repro/307-stage
S306=$TICKET/.scratch/pota-repro/306-stage
RUNS=/data/gpfs/projects/punim2657/SfSpp/runs
ARMS="${ARMS:-base b1 b5 b4}"
CORPUS_ARMS="${CORPUS_ARMS:-base b1}"
TAG="${TAG:-t307a-axes}"

COMMIT=$(git -C "$TICKET" rev-parse --short=7 HEAD)
TS=$("$SSH" spartan 'date -u +%Y%m%d-%H%M')
RUNID="${TS}_${COMMIT}_${TAG}"
RUN="$RUNS/$RUNID"
echo "RUNID=$RUNID"

"$SSH" spartan "mkdir -p $RUN/logs $RUN/work/code $RUN/out"

cd "$TICKET"
rm -rf sfs_axes/__pycache__
cat > "$STAGE/run.json" <<EOF
{
  "runid": "$RUNID",
  "ticket": "307",
  "stage": "B",
  "what": "axis sets: Pot A 4 arms x seeds 0/1/2, corpus 163 pieces in base and b1, A2/C3 tables",
  "template": "307-stage/submit307a.sbatch",
  "commit": "$COMMIT",
  "arms": "$ARMS",
  "corpus_arms": "$CORPUS_ARMS",
  "env": {
    "base": "SFS_AXES_COST_PRUNE=1 (shipped default)",
    "b1": "SFS_AXES_COST_PRUNE=0 (the paper set: no cost<cost[0]*1.1 prune)",
    "b5": "SFS_AXES_ADAPTIVE_UNDER_5K=0 (step=10 always)",
    "b4": "SFS_AXES_POST_REFINE_COST=1 (rank on all-point cost)"
  },
  "corpus": "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp (read-only; md5 before/after)",
  "note": "axes only; no assembly here"
}
EOF

"$SCP" "$STAGE/run.json" "spartan:$RUN/run.json"
"$SCP" "$STAGE/submit307a.sbatch" "spartan:$RUN/submit.sbatch"
"$SCP" -r sfs_axes "spartan:$RUN/work/code/"
"$SCP" "$STAGE/census307.py" "spartan:$RUN/work/"
"$SCP" "$S306/analyse306c.py" "spartan:$RUN/work/"
"$SCP" "$S306/idx_append.py" spartan:/tmp/idx_append.py

OUT=$("$SSH" spartan "cd $RUN && md5sum submit.sbatch && md5sum work/code/sfs_axes/*.py && ARMS='$ARMS' CORPUS_ARMS='$CORPUS_ARMS' sbatch --export=ALL,ARMS='$ARMS',CORPUS_ARMS='$CORPUS_ARMS' submit.sbatch")
echo "$OUT"
JOB=$(echo "$OUT" | sed -n 's/^Submitted batch job \([0-9]*\)$/\1/p')
[ -n "$JOB" ] || { echo "no job id"; exit 1; }
echo "JOB=$JOB  RUN=$RUN"

"$SSH" spartan "python3 /tmp/idx_append.py $RUNID $JOB $COMMIT $TAG"
echo "poll: /c/Windows/System32/OpenSSH/ssh.exe spartan 'sacct -j $JOB --format=State,ExitCode'"
