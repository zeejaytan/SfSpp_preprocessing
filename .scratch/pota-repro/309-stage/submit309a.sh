#!/bin/bash
# Ticket 309 Stage A launcher: V3 B-spline surfaces + A1-A3 on V1/V2/V3.
set -euo pipefail
SSH="/c/Windows/System32/OpenSSH/ssh.exe"
SCP="/c/Windows/System32/OpenSSH/scp.exe"
WT=C:/PR/worktrees/sfs/309
STAGE=$WT/.scratch/pota-repro/309-stage
RUNS=/data/gpfs/projects/punim2657/SfSpp/runs
TAG="${TAG:-t309a-axes}"

COMMIT=$(git -C "$WT" rev-parse --short=7 HEAD)
TS=$("$SSH" spartan 'date -u +%Y%m%d-%H%M')
RUNID="${TS}_${COMMIT}_${TAG}"
RUN="$RUNS/$RUNID"
echo "RUNID=$RUNID"

"$SSH" spartan "mkdir -p $RUN/logs $RUN/work $RUN/out"

cd "$WT"
rm -rf sfs_axes/__pycache__
cat > /tmp/run309a.json <<EOF
{
  "runid": "$RUNID",
  "ticket": "309",
  "stage": "A: stationarity of the 44 released axis lines on V1/V2/V3, Pottmann residual, per-point cost vs our best line",
  "template": "309-stage/submit309a.sbatch",
  "commit": "$COMMIT",
  "variants": {
    "V1": "shipped Surfaces/, walls whole (truncate off)",
    "V2": "read_surfaces.m truncate: both walls cut to the shorter wall",
    "V3": "B-spline resampled surfaces, our implementation (bspline309.py), paper sfspp-2502.13986v1.md:155"
  },
  "pieces": "A_07 D_17 D_24 D_30 E_21 E_31 E_34 F_07 H_06 H_09 J_11 J_13 J_14",
  "corpus": "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp (read-only; 652-path md5 before/after)",
  "note": "axes only; no assembly here"
}
EOF

"$SCP" /tmp/run309a.json "spartan:$RUN/run.json"
sed 's/\r$//' "$STAGE/submit309a.sbatch" > /tmp/submit309a_LF.sbatch
"$SCP" /tmp/submit309a_LF.sbatch "spartan:$RUN/submit.sbatch"
"$SCP" -r sfs_axes "spartan:$RUN/work/"
"$SCP" "$STAGE/stagea309.py" "$STAGE/bspline309.py" "spartan:$RUN/work/"
echo -n "$COMMIT" > /tmp/code_commit.txt
"$SCP" /tmp/code_commit.txt "spartan:$RUN/work/code_commit.txt"

OUT=$("$SSH" spartan "cd $RUN && md5sum submit.sbatch work/*.py work/sfs_axes/*.py && sbatch --parsable submit.sbatch")
echo "$OUT"
JOB=$(echo "$OUT" | tail -1 | tr -d ' ')
echo "JOB=$JOB  RUN=$RUN"
cp "$WT/.scratch/pota-repro/306-stage/idx_append.py" /tmp/idx_append.py
"$SCP" /tmp/idx_append.py spartan:/tmp/idx_append.py
"$SSH" spartan "python3 /tmp/idx_append.py $RUNID $JOB $COMMIT $TAG"
echo "poll: /c/Windows/System32/OpenSSH/ssh.exe spartan 'sacct -j $JOB --format=State,ExitCode'"
