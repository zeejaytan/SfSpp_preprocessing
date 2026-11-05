#!/bin/bash
# Ticket 310 stage B3/C3 launcher. ONLY="stem,stem" limits the run (timing probe).
set -euo pipefail
export MSYS_NO_PATHCONV=1 MSYS2_ARG_CONV_EXCL='*'
SSH="/c/Windows/System32/OpenSSH/ssh.exe"
SCP="/c/Windows/System32/OpenSSH/scp.exe"
WT=C:/PR/worktrees/sfs/310
STAGE="$WT/.scratch/pota-repro/310-stage"
RUNS=/data/gpfs/projects/punim2657/SfSpp/runs
TAG="${TAG:-t310b3-corpus}"
LT="$(cygpath -w /tmp)"

COMMIT=$(git -C "$WT" rev-parse --short=7 HEAD)
TS=$("$SSH" spartan 'date -u +%Y%m%d-%H%M')
RUNID="${TS}_${COMMIT}_${TAG}"
RUN="$RUNS/$RUNID"
echo "RUNID=$RUNID"

"$SSH" spartan "mkdir -p $RUN/logs $RUN/work $RUN/out"
cd "$WT"
rm -rf sfs_axes/__pycache__ .scratch/pota-repro/310-stage/__pycache__
cat > /tmp/run310d.json <<EOF
{
  "runid": "$RUNID",
  "ticket": "310",
  "stage": "B3/C3: every corpus piece through the basin rule (run_potsac_union, SFS_AXES_CONVERGE_BEFORE_RANK=1, 10 seeds, cap 6), axes written to out/axes310/ -- a new path, never the corpus",
  "template": "310-stage/submit310d.sbatch",
  "commit": "$COMMIT",
  "only": "${ONLY:-all}",
  "corpus": "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp (read-only)",
  "note": "axes only; no assembly here"
}
EOF
"$SCP" "$LT\\run310d.json" "spartan:$RUN/run.json"
sed 's/\r$//' "$STAGE/submit310d.sbatch" > /tmp/submit310d_LF.sbatch
"$SCP" "$LT\\submit310d_LF.sbatch" "spartan:$RUN/submit.sbatch"
"$SCP" -r sfs_axes "spartan:$RUN/work/"
"$SCP" "$STAGE/corpus310.py" "spartan:$RUN/work/"
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
