#!/bin/bash
set -euo pipefail
export MSYS_NO_PATHCONV=1 MSYS2_ARG_CONV_EXCL='*'
SSH="/c/Windows/System32/OpenSSH/ssh.exe"
SCP="/c/Windows/System32/OpenSSH/scp.exe"
WT=C:/PR/worktrees/sfs/311
STAGE="$WT/.scratch/pota-repro/311-stage"
S305="$WT/.scratch/pota-repro/305-stage"
S306="$WT/.scratch/pota-repro/306-stage"
RUNS=/data/gpfs/projects/punim2657/SfSpp/runs
TAG="t311b-kladder-E"
LT="$(cygpath -w /tmp)"

COMMIT=$(git -C "$WT" rev-parse --short=7 HEAD)
TS=$("$SSH" -T -o BatchMode=yes spartan 'date -u +%Y%m%d-%H%M')
RUNID="${TS}_${COMMIT}_${TAG}"
RUN="$RUNS/$RUNID"
echo "RUNID=$RUNID"

"$SSH" -T -o BatchMode=yes spartan "mkdir -p $RUN/logs $RUN/work $RUN/out $RUN/score $RUN/trees"
cd "$WT"
rm -rf /tmp/s311bwork && mkdir -p /tmp/s311bwork
cp "$S305/arm67.sh" "$S305/patch_guard67.py" "$S305/mk_inc.py" "$S305/stage305.py" \
   "$S305/acc305.py" "$S305/score305.py" "$S306/idx_append.py" \
   "$STAGE/score311_cpp.py" "$STAGE/summarise311b.py" "$STAGE/submit311b.sbatch" /tmp/s311bwork/
sed -i 's/\r$//' /tmp/s311bwork/*
if grep -l "$(printf '\r')" /tmp/s311bwork/* >/dev/null 2>&1; then echo "ABORT: CR survived"; exit 1; fi
echo -n "$COMMIT" > /tmp/code_commit.txt

cat > /tmp/run311b.json <<EOF
{
  "runid": "$RUNID",
  "ticket": "311",
  "stage": "B: Pot E K-ladder (E_K1, E_K2, E_K3, E_K6) + controls (E_MO, E_BASE), 2 repeats each, in one allocation",
  "template": "311-stage/submit311b.sbatch",
  "commit": "$COMMIT",
  "pot": "E",
  "named": 31,
  "np": 31,
  "floor": 50,
  "arms": ["E_MO:2", "E_BASE:2", "E_K1:2", "E_K2:2", "E_K3:2", "E_K6:2"],
  "axes": {
    "E_MO": "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp/Axes",
    "E_BASE": "/data/gpfs/projects/punim2657/SfSpp/runs/20261105-0532_d330469_t308a-axes/out/axes_paper",
    "E_K1..K6": "head -n K of /data/gpfs/projects/punim2657/SfSpp/runs/20261105-1215_1a6f16e_t310b3-timing/out/axes310"
  },
  "corpus": "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp (read-only)"
}
EOF

"$SCP" "$LT\\run311b.json" "spartan:$RUN/run.json"
"$SCP" "$LT\\s311bwork\\submit311b.sbatch" "spartan:$RUN/submit.sbatch"
for f in arm67.sh patch_guard67.py mk_inc.py stage305.py acc305.py score305.py idx_append.py score311_cpp.py summarise311b.py; do
  "$SCP" "$LT\\s311bwork\\$f" "spartan:$RUN/work/$f"
done
"$SCP" "$LT\\code_commit.txt" "spartan:$RUN/work/code_commit.txt"

OUT=$("$SSH" -T -o BatchMode=yes spartan "cd $RUN && md5sum submit.sbatch work/*.py work/*.sh | tee logs/instruments.md5 && sbatch --parsable submit.sbatch > sbatch.id && cat sbatch.id")
echo "$OUT"
JOB=$(echo "$OUT" | tail -1 | tr -d ' \r')
echo "JOB=$JOB  RUN=$RUN"
"$SSH" -T -o BatchMode=yes spartan "python3 $RUN/work/idx_append.py $RUNID $JOB $COMMIT $TAG"
