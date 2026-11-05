#!/bin/bash
# Ticket 310 B2 probe on two large pieces: does converge-before-rank ever change the
# answer away from the union path without it? (On Pot A Piece 08 it did not: 24/24).
set -euo pipefail
export MSYS_NO_PATHCONV=1 MSYS2_ARG_CONV_EXCL='*'
SSH=/c/Windows/System32/OpenSSH/ssh.exe
SCP=/c/Windows/System32/OpenSSH/scp.exe
WT=C:/PR/worktrees/sfs/310
STAGE="$WT/.scratch/pota-repro/310-stage"
RUNS=/data/gpfs/projects/punim2657/SfSpp/runs
ARMS="${ARMS:-UNION0,BASIN}"
SEEDS="${SEEDS:-0:6}"
CAP="${CAP:-6}"
JOBS="${JOBS:-6}"
POT="${POT:-D}"
PIECES="${PIECES:-1,3}"
TAG="${TAG:-t310b2-big}"
LT=$(cygpath -w /tmp)
COMMIT=$(git -C "$WT" rev-parse --short=7 HEAD)
TS=$("$SSH" spartan 'date -u +%Y%m%d-%H%M')
RUNID="${TS}_${COMMIT}_${TAG}"
RUN="$RUNS/$RUNID"
echo "RUNID=$RUNID pot=$POT pieces=$PIECES arms=$ARMS seeds=$SEEDS cap=$CAP"
"$SSH" spartan "mkdir -p $RUN/logs $RUN/work $RUN/out"
cd "$WT" && rm -rf sfs_axes/__pycache__
sed -e "s|__ARMS__|$ARMS|" -e "s|__SEEDS__|$SEEDS|" -e "s|__CAP__|$CAP|" -e "s|__JOBS__|$JOBS|" -e "s|__POT__|$POT|" -e "s|__PIECES__|$PIECES|" "$STAGE/submit310j.sbatch" | sed 's/\r$//' > /tmp/submit310j.sbatch
cat > /tmp/run310j.json <<EOF
{
  "runid": "$RUNID",
  "ticket": "310",
  "stage": "B2 probe on Pot D 01 and 03: arms=$ARMS seeds=$SEEDS cap=$CAP -- does converge-before-rank change the written axis on pieces that are not Pot A Piece 08?",
  "template": "310-stage/submit310j.sbatch",
  "commit": "$COMMIT",
  "corpus": "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp (read-only)"
}
EOF
"$SCP" "$LT\\run310j.json" "spartan:$RUN/run.json"
"$SCP" "$LT\\submit310j.sbatch" "spartan:$RUN/submit.sbatch"
"$SCP" -r sfs_axes "spartan:$RUN/work/"
"$SCP" "$STAGE/stage310b2.py" "spartan:$RUN/work/"
echo -n "$COMMIT" > /tmp/code_commit.txt
"$SCP" "$LT\\code_commit.txt" "spartan:$RUN/work/code_commit.txt"
OUT=$("$SSH" spartan "cd $RUN && grep -n '^ARMS=\|^PIECES=\|^CAP=\|^SEEDS=' submit.sbatch; md5sum submit.sbatch work/*.py | tee logs/instruments.md5; sbatch --parsable submit.sbatch")
echo "$OUT"
JOB=$(echo "$OUT" | tail -1 | tr -d ' ')
echo "JOB=$JOB RUN=$RUN"
cp "$WT/.scratch/pota-repro/306-stage/idx_append.py" /tmp/idx_append.py
"$SCP" "$LT\\idx_append.py" spartan:/tmp/idx_append.py
"$SSH" spartan "python3 /tmp/idx_append.py $RUNID $JOB $COMMIT $TAG"