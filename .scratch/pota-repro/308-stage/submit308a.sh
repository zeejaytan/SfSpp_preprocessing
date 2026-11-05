#!/bin/bash
# Ticket 308 Stage A launcher: the MM/MMp/Juglet/seed axis sets + their census.
# Creates the run dir, copies the working tree's sfs_axes and the helpers, submits,
# records the index row.  Nothing is committed by this script.
set -euo pipefail
SSH="/c/Windows/System32/OpenSSH/ssh.exe"
SCP="/c/Windows/System32/OpenSSH/scp.exe"
WT=C:/PR/worktrees/sfs/308
STAGE=$WT/.scratch/pota-repro/308-stage
S306=$WT/.scratch/pota-repro/306-stage
S305=$WT/.scratch/pota-repro/305-stage
S307=$WT/.scratch/pota-repro/307-stage
RUNS=/data/gpfs/projects/punim2657/SfSpp/runs
TAG="${TAG:-t308a-axes}"

COMMIT=$(git -C "$WT" rev-parse --short=7 HEAD)
TS=$("$SSH" spartan 'date -u +%Y%m%d-%H%M')
RUNID="${TS}_${COMMIT}_${TAG}"
RUN="$RUNS/$RUNID"
echo "RUNID=$RUNID"

"$SSH" spartan "mkdir -p $RUN/logs $RUN/work $RUN/out"

cd "$WT"
rm -rf sfs_axes/__pycache__
cat > "$STAGE/run.json.t308a" <<EOF
{
  "runid": "$RUNID",
  "ticket": "308",
  "stage": "A: the axis set at the shipped 308 default, its provenance, the 305 reproduction",
  "template": "308-stage/submit308a.sbatch",
  "commit": "$COMMIT",
  "sets": {
    "axes_paper": "no env: paper chain, walls whole (truncate off), cost prune off, seed 0 -- the 308 MM set",
    "axes_prune": "SFS_AXES_COST_PRUNE=1, everything else the same -- the 308 MMp set",
    "pota/paper_s0..s7": "Pot A only, seeds 0-7, same default -- B4",
    "jug/axes_paper": "Juglet, the same default, from the t66 S0/S1 walls -- Stage C",
    "axes_305repro": "axes305.py --truncate 1 with prune on: must equal 305's axes305 byte for byte"
  },
  "worktree": "C:/PR/worktrees/sfs/308 at $COMMIT",
  "corpus": "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp (read-only; md5 before/after over Axes, Breakline_0 and Surfaces)",
  "note": "axes only; no assembly here"
}
EOF

"$SCP" "$STAGE/run.json.t308a" "spartan:$RUN/run.json"
sed 's/\r$//' "$STAGE/submit308a.sbatch" > /tmp/submit308a_LF.sbatch
"$SCP" /tmp/submit308a_LF.sbatch "spartan:$RUN/submit.sbatch"
"$SCP" -r sfs_axes "spartan:$RUN/work/"
"$SCP" "$S305/axes305.py" "spartan:$RUN/work/"
"$SCP" "$STAGE/census308.py" "spartan:$RUN/work/"
"$SCP" "$S307/census307.py" "spartan:$RUN/work/"
"$SCP" "$S306/analyse306c.py" "spartan:$RUN/work/"
"$SCP" "$S306/idx_append.py" spartan:/tmp/idx_append.py
echo -n "$COMMIT" > /tmp/code_commit.txt
"$SCP" /tmp/code_commit.txt "spartan:$RUN/work/code_commit.txt"
rm -f "$STAGE/run.json.t308a"

OUT=$("$SSH" spartan "cd $RUN && md5sum submit.sbatch work/sfs_axes/*.py work/census308.py work/axes305.py && sbatch --parsable submit.sbatch")
echo "$OUT"
JOB=$(echo "$OUT" | tail -1 | tr -d ' ')
echo "JOB=$JOB  RUN=$RUN"
"$SSH" spartan "python3 /tmp/idx_append.py $RUNID $JOB $COMMIT $TAG"
echo "poll: /c/Windows/System32/OpenSSH/ssh.exe spartan 'sacct -j $JOB --format=State,ExitCode'"
