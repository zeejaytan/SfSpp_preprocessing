#!/bin/bash
# Ticket 310 B2 boundary-test launcher.  ARMS/SEEDS/CAP/JOBS are baked into the
# submitted script with sed: this cluster does not carry the submitter's environment
# into the job (a job submitted with CAP=2 ran with cap=6 -- run 20261105-1223).
set -euo pipefail
export MSYS_NO_PATHCONV=1 MSYS2_ARG_CONV_EXCL='*'
SSH="/c/Windows/System32/OpenSSH/ssh.exe"
SCP="/c/Windows/System32/OpenSSH/scp.exe"
WT=C:/PR/worktrees/sfs/310
STAGE="$WT/.scratch/pota-repro/310-stage"
RUNS=/data/gpfs/projects/punim2657/SfSpp/runs
ARMS="${ARMS:-UNION0,BASIN}"
SEEDS="${SEEDS:-0:12}"
CAP="${CAP:-2}"
JOBS="${JOBS:-7}"
TAG="${TAG:-t310b2-cap}"
LT="$(cygpath -w /tmp)"
COMMIT=$(git -C "$WT" rev-parse --short=7 HEAD)
TS=$("$SSH" spartan 'date -u +%Y%m%d-%H%M')
RUNID="${TS}_${COMMIT}_${TAG}"
RUN="$RUNS/$RUNID"
echo "RUNID=$RUNID arms=$ARMS seeds=$SEEDS cap=$CAP"
"$SSH" spartan "mkdir -p $RUN/logs $RUN/work $RUN/out"
cd "$WT"
rm -rf sfs_axes/__pycache__
sed -e "s|__ARMS__|$ARMS|" -e "s|__SEEDS__|$SEEDS|" -e "s|__CAP__|$CAP|" \
    -e "s|__JOBS__|$JOBS|" "$STAGE/submit310i.sbatch" | sed 's/\r$//' > /tmp/submit310i.sbatch
cat > /tmp/run310i.json <<EOF
{
  "runid": "$RUNID",
  "ticket": "310",
  "stage": "B2 boundary: arms=$ARMS seeds=$SEEDS cap=$CAP on Pot A Piece 08 -- what converge-before-rank buys at a tight candidate budget",
  "template": "310-stage/submit310i.sbatch (arms/seeds/cap baked, not exported)",
  "commit": "$COMMIT",
  "corpus": "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp (read-only)"
}
EOF
"$SCP" "$LT\\run310i.json" "spartan:$RUN/run.json"
"$SCP" "$LT\\submit310i.sbatch" "spartan:$RUN/submit.sbatch"
"$SCP" -r sfs_axes "spartan:$RUN/work/"
"$SCP" "$STAGE/stage310b2.py" "spartan:$RUN/work/"
echo -n "$COMMIT" > /tmp/code_commit.txt
"$SCP" "$LT\\code_commit.txt" "spartan:$RUN/work/code_commit.txt"
A=/data/gpfs/projects/punim2657/SfSpp/runs/20261105-1144_1a6f16e_t310a-stage
"$SCP" "spartan:$A/work/good310.xyz" "spartan:$RUN/work/good310.xyz"
OUT=$("$SSH" spartan "cd $RUN && grep -n '^ARMS=\|^CAP=' submit.sbatch && md5sum submit.sbatch work/*.py work/sfs_axes/*.py | tee logs/instruments.md5 && sbatch --parsable submit.sbatch")
echo "$OUT"
JOB=$(echo "$OUT" | tail -1 | tr -d ' ')
echo "JOB=$JOB  RUN=$RUN"
cp "$WT/.scratch/pota-repro/306-stage/idx_append.py" /tmp/idx_append.py
"$SCP" "$LT\\idx_append.py" spartan:/tmp/idx_append.py
"$SSH" spartan "python3 /tmp/idx_append.py $RUNID $JOB $COMMIT $TAG"
