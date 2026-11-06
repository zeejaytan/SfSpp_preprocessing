#!/bin/bash
set -euo pipefail
export MSYS_NO_PATHCONV=1 MSYS2_ARG_CONV_EXCL='*'
SSH="/c/Windows/System32/OpenSSH/ssh.exe"
SCP="/c/Windows/System32/OpenSSH/scp.exe"
WT=C:/PR/worktrees/sfs/311
STAGE="$WT/.scratch/pota-repro/311-stage"
RUNS=/data/gpfs/projects/punim2657/SfSpp/runs
TAG="t311cd-basins"
LT="$(cygpath -w /tmp)"

COMMIT=$(git -C "$WT" rev-parse --short=7 HEAD)
TS=$("$SSH" -T -o BatchMode=yes spartan 'date -u +%Y%m%d-%H%M')
RUNID="${TS}_${COMMIT}_${TAG}"
RUN="$RUNS/$RUNID"
echo "RUNID=$RUNID"

"$SSH" -T -o BatchMode=yes spartan "mkdir -p $RUN/logs $RUN/work $RUN/out"
cd "$WT"
rm -rf sfs_axes/__pycache__
cat > /tmp/run311cd.json <<EOF
{
  "runid": "$RUNID",
  "ticket": "311",
  "stage": "C+D: Pot E all-candidates basin tables & stationarity + 163-piece blind-cap corpus sweep",
  "template": "311-stage/submit311cd.sbatch",
  "commit": "$COMMIT",
  "corpus": "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp (read-only)"
}
EOF
"$SCP" "$LT\\run311cd.json" "spartan:$RUN/run.json"
sed 's/\r$//' "$STAGE/submit311cd.sbatch" > /tmp/submit311cd_LF.sbatch
"$SCP" "$LT\\submit311cd_LF.sbatch" "spartan:$RUN/submit.sbatch"
"$SCP" -r sfs_axes "spartan:$RUN/work/"
sed 's/\r$//' "$STAGE/stage311cd.py" > /tmp/stage311cd_LF.py
"$SCP" "$LT\\stage311cd_LF.py" "spartan:$RUN/work/stage311cd.py"
echo -n "$COMMIT" > /tmp/code_commit.txt
"$SCP" "$LT\\code_commit.txt" "spartan:$RUN/work/code_commit.txt"

OUT=$("$SSH" -T -o BatchMode=yes spartan "cd $RUN && md5sum submit.sbatch work/*.py work/sfs_axes/*.py | tee logs/instruments.md5 && sbatch --parsable submit.sbatch")
echo "$OUT"
JOB=$(echo "$OUT" | tail -1 | tr -d ' \r')
echo "JOB=$JOB  RUN=$RUN"
cp "$WT/.scratch/pota-repro/306-stage/idx_append.py" /tmp/idx_append.py
sed -i 's/\r$//' /tmp/idx_append.py
"$SCP" "$LT\\idx_append.py" spartan:/tmp/idx_append.py
"$SSH" -T -o BatchMode=yes spartan "python3 /tmp/idx_append.py $RUNID $JOB $COMMIT $TAG"
