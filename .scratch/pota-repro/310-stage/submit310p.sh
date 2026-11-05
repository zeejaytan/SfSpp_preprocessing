#!/bin/bash
# Ticket 310 B4 parity launcher: HEAD package vs the worktree package with
# SFS_AXES_CONVERGE_BEFORE_RANK=0, same pool, same seeds, compared to the last bit.
set -euo pipefail
export MSYS_NO_PATHCONV=1 MSYS2_ARG_CONV_EXCL='*'
SSH="/c/Windows/System32/OpenSSH/ssh.exe"
SCP="/c/Windows/System32/OpenSSH/scp.exe"
WT=C:/PR/worktrees/sfs/310
STAGE="$WT/.scratch/pota-repro/310-stage"
RUNS=/data/gpfs/projects/punim2657/SfSpp/runs
POT="${POT:-A}"
PIECES="${PIECES:-8}"
SEEDS="${SEEDS:-0:3}"
CAP="${CAP:-6}"
SWOFF="${SWOFF:-0}"
TAG="${TAG:-t310p-offparity}"
LT="$(cygpath -w /tmp)"
COMMIT=$(git -C "$WT" rev-parse --short=7 HEAD)
TS=$("$SSH" spartan 'date -u +%Y%m%d-%H%M')
RUNID="${TS}_${COMMIT}_${TAG}"
RUN="$RUNS/$RUNID"
echo "RUNID=$RUNID pot=$POT pieces=$PIECES seeds=$SEEDS cap=$CAP switch_off=$SWOFF"
"$SSH" spartan "mkdir -p $RUN/logs $RUN/work $RUN/out"
cd "$WT"
rm -rf sfs_axes/__pycache__
# the worktree package, and a copy whose potsac.py is the base commit's
rm -rf /tmp/s310p && mkdir -p /tmp/s310p/new/sfs_axes /tmp/s310p/head/sfs_axes
cp sfs_axes/*.py /tmp/s310p/new/sfs_axes/
cp sfs_axes/*.py /tmp/s310p/head/sfs_axes/
git show HEAD:sfs_axes/potsac.py > /tmp/s310p/head/sfs_axes/potsac.py
diff -q /tmp/s310p/head/sfs_axes/potsac.py /tmp/s310p/new/sfs_axes/potsac.py || true
cp "$STAGE/stage310p.py" "$STAGE/cmp310p.py" /tmp/s310p/
sed -i 's/\r$//' /tmp/s310p/*.py /tmp/s310p/new/sfs_axes/*.py /tmp/s310p/head/sfs_axes/*.py
sed -e "s|__POT__|$POT|" -e "s|__PIECES__|$PIECES|" -e "s|__SEEDS__|$SEEDS|" \
    -e "s|__CAP__|$CAP|" -e "s|__SWOFF__|$SWOFF|" "$STAGE/submit310p.sbatch" \
    | sed 's/\r$//' > /tmp/submit310p.sbatch
cat > /tmp/run310p.json <<EOF
{
  "runid": "$RUNID",
  "ticket": "310",
  "stage": "B4: is SFS_AXES_CONVERGE_BEFORE_RANK=$SWOFF identical to the base commit's union path? pot=$POT pieces=$PIECES seeds=$SEEDS cap=$CAP",
  "template": "310-stage/submit310p.sbatch",
  "commit": "$COMMIT",
  "corpus": "/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp (read-only)"
}
EOF
"$SCP" "$LT\\run310p.json" "spartan:$RUN/run.json"
"$SCP" "$LT\\submit310p.sbatch" "spartan:$RUN/submit.sbatch"
P=$(cygpath -w /tmp/s310p)
"$SCP" -r "$P\\new" "spartan:$RUN/work/new"
"$SCP" -r "$P\\head" "spartan:$RUN/work/head"
"$SCP" "$P\\stage310p.py" "$P\\cmp310p.py" "spartan:$RUN/work/"
echo -n "$COMMIT" > /tmp/code_commit.txt
"$SCP" "$LT\\code_commit.txt" "spartan:$RUN/work/code_commit.txt"
"$SCP" "spartan:$RUNS/20261105-1144_1a6f16e_t310a-stage/work/good310.xyz" "spartan:$RUN/work/good310.xyz"
OUT=$("$SSH" spartan "cd $RUN && grep -n '^SEEDS=\|^SWITCH_OFF=' submit.sbatch && md5sum submit.sbatch work/*.py | tee logs/instruments.md5 && sbatch --parsable submit.sbatch")
echo "$OUT"
JOB=$(echo "$OUT" | tail -1 | tr -d ' ')
echo "JOB=$JOB RUN=$RUN"
cp "$WT/.scratch/pota-repro/306-stage/idx_append.py" /tmp/idx_append.py
"$SCP" "$LT\\idx_append.py" spartan:/tmp/idx_append.py
"$SSH" spartan "python3 /tmp/idx_append.py $RUNID $JOB $COMMIT $TAG"
