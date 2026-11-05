#!/bin/bash
# Ticket 310 Stage A launcher: Piece A_08 x 24 seeds + A_01/A_04 controls.
set -euo pipefail
export MSYS_NO_PATHCONV=1 MSYS2_ARG_CONV_EXCL='*'
SSH="/c/Windows/System32/OpenSSH/ssh.exe"
SCP="/c/Windows/System32/OpenSSH/scp.exe"
WT=C:/PR/worktrees/sfs/310
STAGE="$WT/.scratch/pota-repro/310-stage"
RUNS=/data/gpfs/projects/punim2657/SfSpp/runs
TAG="${TAG:-t310a-stage}"
LT="$(cygpath -w /tmp)"     # scp here is a Windows binary; conversion is off, so local paths must be Windows

COMMIT=$(git -C "$WT" rev-parse --short=7 HEAD)
TS=$("$SSH" spartan 'date -u +%Y%m%d-%H%M')
RUNID="${TS}_${COMMIT}_${TAG}"
RUN="$RUNS/$RUNID"
echo "RUNID=$RUNID"

"$SSH" spartan "mkdir -p $RUN/logs $RUN/work $RUN/out"

cd "$WT"
rm -rf sfs_axes/__pycache__ .scratch/pota-repro/310-stage/__pycache__
cat > /tmp/run310a.json <<EOF
{
  "runid": "$RUNID",
  "ticket": "310",
  "stage": "A: piece A_08 x 24 seeds + A_01/A_04 x 16 seeds -- written-file lines and 10-deg basins measured on the piece's own two surfaces (per-wall cost, inliers, Pottmann residual, cross-wall agreement, radius profile, placement, pool occupancy)",
  "template": "310-stage/submit310a.sbatch",
  "commit": "$COMMIT",
  "reused_instrument": "306-stage/probe306.py (pool dump) extended into 310-stage/stage310a.py",
  "label_reference": "work/good310.xyz = the axis that seated in ticket 308 (piece 08 seeds 1/4/5)",
  "corpus": "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp (read-only; 652-path md5 before/after)",
  "note": "axes only; no assembly here"
}
EOF

"$SCP" "$LT\\run310a.json" "spartan:$RUN/run.json"
sed 's/\r$//' "$STAGE/submit310a.sbatch" > /tmp/submit310a_LF.sbatch
"$SCP" "$LT\\submit310a_LF.sbatch" "spartan:$RUN/submit.sbatch"
"$SCP" -r sfs_axes "spartan:$RUN/work/"
"$SCP" "$STAGE/stage310a.py" "spartan:$RUN/work/"
echo -n "$COMMIT" > /tmp/code_commit.txt
"$SCP" "$LT\\code_commit.txt" "spartan:$RUN/work/code_commit.txt"

OUT=$("$SSH" spartan "cd $RUN && md5sum submit.sbatch work/*.py work/sfs_axes/*.py | tee logs/instruments.md5 && sbatch --parsable submit.sbatch")
echo "$OUT"
JOB=$(echo "$OUT" | tail -1 | tr -d ' ')
echo "JOB=$JOB  RUN=$RUN"
cp "$WT/.scratch/pota-repro/306-stage/idx_append.py" /tmp/idx_append.py
"$SCP" "$LT\\idx_append.py" spartan:/tmp/idx_append.py
"$SSH" spartan "python3 /tmp/idx_append.py $RUNID $JOB $COMMIT $TAG"
echo "poll: /c/Windows/System32/OpenSSH/ssh.exe spartan 'sacct -j $JOB --format=State,ExitCode'"
