#!/bin/bash
# Ticket 310 A4(iii) launcher.
set -euo pipefail
export MSYS_NO_PATHCONV=1 MSYS2_ARG_CONV_EXCL='*'
SSH="/c/Windows/System32/OpenSSH/ssh.exe"
SCP="/c/Windows/System32/OpenSSH/scp.exe"
WT=C:/PR/worktrees/sfs/310
STAGE="$WT/.scratch/pota-repro/310-stage"
RUNS=/data/gpfs/projects/punim2657/SfSpp/runs
TAG="${TAG:-t310a4iii-pool}"
LT="$(cygpath -w /tmp)"
COMMIT=$(git -C "$WT" rev-parse --short=7 HEAD)
TS=$("$SSH" spartan 'date -u +%Y%m%d-%H%M')
RUNID="${TS}_${COMMIT}_${TAG}"
RUN="$RUNS/$RUNID"
echo "RUNID=$RUNID"
"$SSH" spartan "mkdir -p $RUN/logs $RUN/work $RUN/out"
cd "$WT"
rm -rf sfs_axes/__pycache__
cat > /tmp/run310h.json <<EOF
{
  "runid": "$RUNID",
  "ticket": "310",
  "stage": "A4(iii): 10 000 draws instead of 1000, A_08 x 3 seeds; does a bigger pool put a seating draw into the shipped top-10 shortlist",
  "template": "310-stage/submit310h.sbatch",
  "commit": "$COMMIT",
  "corpus": "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp (read-only)"
}
EOF
"$SCP" "$LT\\run310h.json" "spartan:$RUN/run.json"
sed 's/\r$//' "$STAGE/submit310h.sbatch" > /tmp/submit310h_LF.sbatch
"$SCP" "$LT\\submit310h_LF.sbatch" "spartan:$RUN/submit.sbatch"
"$SCP" -r sfs_axes "spartan:$RUN/work/"
"$SCP" "$STAGE/stage310h.py" "spartan:$RUN/work/"
echo -n "$COMMIT" > /tmp/code_commit.txt
"$SCP" "$LT\\code_commit.txt" "spartan:$RUN/work/code_commit.txt"
A=/data/gpfs/projects/punim2657/SfSpp/runs/20261105-1144_1a6f16e_t310a-stage
"$SCP" "spartan:$A/work/good310.xyz" "spartan:$RUN/work/good310.xyz"
OUT=$("$SSH" spartan "cd $RUN && md5sum submit.sbatch work/*.py work/sfs_axes/*.py | tee logs/instruments.md5 && sbatch --parsable submit.sbatch")
echo "$OUT"
JOB=$(echo "$OUT" | tail -1 | tr -d ' ')
echo "JOB=$JOB  RUN=$RUN"
cp "$WT/.scratch/pota-repro/306-stage/idx_append.py" /tmp/idx_append.py
"$SCP" "$LT\\idx_append.py" spartan:/tmp/idx_append.py
"$SSH" spartan "python3 /tmp/idx_append.py $RUNID $JOB $COMMIT $TAG"
