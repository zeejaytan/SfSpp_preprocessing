#!/bin/bash
set -euo pipefail
export MSYS_NO_PATHCONV=1 MSYS2_ARG_CONV_EXCL='*'
SSH="/c/Windows/System32/OpenSSH/ssh.exe"
SCP="/c/Windows/System32/OpenSSH/scp.exe"

WT=C:/PR/worktrees/sfs/311
S311=$WT/.scratch/pota-repro/311-stage
S305=$WT/.scratch/pota-repro/305-stage
S306=$WT/.scratch/pota-repro/306-stage
RUNS=/data/gpfs/projects/punim2657/SfSpp/runs
COMMIT=$(git -C "$WT" rev-parse --short=7 HEAD)
TAG="t311b2-kladder-K23"

TS=$("$SSH" -T -o BatchMode=yes spartan "date -u +%Y%m%d-%H%M")
RUNID="${TS}_${COMMIT}_${TAG}"
RUN="$RUNS/$RUNID"
echo "== Submitting $RUNID"

"$SSH" -T -o BatchMode=yes spartan "mkdir -p $RUN/logs $RUN/work $RUN/out $RUN/score"

cat > "$S311/run311b2.json" <<EOF
{
  "runid": "$RUNID",
  "ticket": "311",
  "stage": "B (companion): Pot E K2 & K3 on 4 dedicated 12-CPU slices",
  "commit": "$COMMIT",
  "pot": "E",
  "named": 31,
  "np": 31,
  "floor": 50,
  "arms": ["E_K2", "E_K3"],
  "repeats": 2
}
EOF

echo -n "$COMMIT" > "$S311/code_commit.txt"
sed -i 's/\r$//' "$S311/submit311b2.sbatch" "$S311/score311_cpp.py" "$S311/summarise311b.py" "$S311/run311b2.json"

"$SCP" -q -o BatchMode=yes "$S311/run311b2.json" "spartan:$RUN/run.json"
"$SCP" -q -o BatchMode=yes "$S311/submit311b2.sbatch" "spartan:$RUN/submit.sbatch"
"$SCP" -q -o BatchMode=yes "$S311/code_commit.txt" "spartan:$RUN/work/code_commit.txt"
"$SCP" -q -o BatchMode=yes "$S311/score311_cpp.py" "spartan:$RUN/work/score311_cpp.py"
"$SCP" -q -o BatchMode=yes "$S311/summarise311b.py" "spartan:$RUN/work/summarise311b.py"

for f in arm67.sh patch_guard67.py mk_inc.py stage305.py acc305.py score305.py; do
  "$SCP" -q -o BatchMode=yes "$S305/$f" "spartan:$RUN/work/$f"
done
"$SCP" -q -o BatchMode=yes "$S306/idx_append.py" "spartan:$RUN/work/idx_append.py"

JOB=$("$SSH" -T -o BatchMode=yes spartan "cd $RUN && sed -i 's/\r$//' submit.sbatch work/*.sh work/*.py && sbatch --parsable submit.sbatch | tee sbatch.id" | tail -1 | tr -d ' \r')
echo "   JOB=$JOB"
"$SSH" -T -o BatchMode=yes spartan "python3 $RUN/work/idx_append.py $RUNID $JOB $COMMIT $TAG"
