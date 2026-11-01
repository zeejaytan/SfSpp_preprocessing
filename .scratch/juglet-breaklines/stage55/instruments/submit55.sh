#!/usr/bin/env bash
# submit55.sh -- laptop-side submitter for ticket 55 (run FROM stage55/instruments/).
# Gates first (CRLF, py_compile, bash -n, placeholder, expansion count), renders the
# sbatch template, pushes the instruments to the run directory on Spartan, submits, and
# records run.json + jobid.txt.  Adapts submit54.sh; Spartan only receives, never edits.
set -euo pipefail

INSTR=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$INSTR/../../../.." && pwd)          # the repo worktree root
PY=python
SSH=spartan
RUNS=/data/gpfs/projects/punim2657/SfSpp/runs
TAG=t55-worness07-breaklines
TIME=03:30:00

cd "$ROOT"
BR=$(git rev-parse --abbrev-ref HEAD)
HEAD=$(git rev-parse HEAD)
echo "[S55] branch=$BR head=$HEAD"
[ "$(git status --porcelain | wc -l)" -eq 0 ] || { echo "[S55] worktree not clean -- commit first"; exit 1; }
git fetch -q origin
PUSHED=$(git rev-parse "origin/$BR" 2>/dev/null || true)
[ "$PUSHED" = "$HEAD" ] || { echo "[S55] HEAD not pushed to origin/$BR"; exit 1; }
BR7=${HEAD:0:7}
RUNID=$(date +%Y%m%d-%H%M)_${BR7}_${TAG}
RUNDIR=$RUNS/$RUNID
echo "[S55] runid=$RUNID"

# gates -- the paid-for failure modes, checked before anything leaves the laptop
cd "$INSTR"
for f in *.sh *.py *.tmpl; do
  grep -qU $'\r' "$f" && { echo "[S55] CRLF in $f"; exit 1; };
done
"$PY" -m py_compile render55.py || { echo "[S55] py_compile render55.py failed"; exit 1; }
bash -n run_cell55.sh || { echo "[S55] bash -n run_cell55.sh failed"; exit 1; }

# MSYS path conversion rewrites argv that look like POSIX roots (/data/...) into the
# bash-win32 install prefix, which once baked C:/Users/... into --output and RUN= and
# failed the job at the instruments gate (job 34165338).  Exclude every arg here.
MSYS2_ARG_CONV_EXCL='*' MSYS_NO_PATHCONV=1 "$PY" - "$INSTR/submit55.sbatch.tmpl" "$INSTR/submit.sbatch" "$RUNID" "$RUNDIR" "$HEAD" "$TAG" "$TIME" <<'PYEOF'
import sys
tmpl, out, runid, rundir, new, tag, time = sys.argv[1:8]
s = open(tmpl, encoding="utf-8").read()
for k, v in [("__JOBNAME__", "t55-brk"), ("__RUNID__", runid), ("__RUNDIR__", rundir),
             ("__NEWCOMMIT__", new), ("__IXTAG__", tag), ("__TIME__", time)]:
    s = s.replace(k, v)
open(out, "w", encoding="utf-8", newline="\n").write(s)
print("rendered", out, len(s), "bytes")
PYEOF

grep -q '__[A-Z0-9]*__' submit.sbatch && { echo "[S55] unreplaced placeholder in submit.sbatch"; exit 1; };
bash -n submit.sbatch || { echo "[S55] bash -n submit.sbatch failed"; exit 1; }
EXP=$(grep -o '\$' submit.sbatch | wc -l)
[ "$EXP" -ge 40 ] || { echo "[S55] only $EXP variable refs in submit.sbatch -- render broken?"; exit 1; };
# a Windows-mangled path in the render is fatal, not cosmetic: on the compute node it
# becomes a literal 'C:' tree inside the rundir and the job dies at a gate
if grep -q 'C:' "$INSTR/submit.sbatch"; then grep -n 'C:' "$INSTR/submit.sbatch" | head -3; echo "[S55] submit.sbatch carries a Windows-mangled path"; exit 1; fi
echo "[S55] gates passed (expansions=$EXP)"

# push instruments + rendered sbatch, submit
ssh "$SSH" "mkdir -p '$RUNDIR/logs' '$RUNDIR/instruments'"
# every *.py *.sh *.tsv in instruments/ must ship: the job md5-compares its whole
# rundir instrument set against the git archive of the pushed commit
tar -C "$INSTR" -cf - .gitattributes check-stage55.sh render55.py run_cell55.sh stage_synth_p40.sh submit55.sbatch.tmpl submit55.sh | ssh "$SSH" "tar -C '$RUNDIR/instruments' -xf -"
scp -q "$INSTR/submit.sbatch" "$SSH:$RUNDIR/submit.sbatch"

JOBID=$(ssh "$SSH" "sbatch --parsable '$RUNDIR/submit.sbatch'")
echo "[S55] JOBID=$JOBID"

ssh "$SSH" "printf '%s' '$JOBID' > '$RUNDIR/jobid.txt'; \
  printf '{\"runid\": \"%s\", \"jobid\": \"%s\", \"commit\": \"%s\", \"tag\": \"%s\", \"branch\": \"%s\", \"worness\": 0.7, \"pieces\": 9, \"submitted_utc\": \"%s\"}\n' \
  '$RUNID' '$JOBID' '$HEAD' '$TAG' '$BR' \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\" > '$RUNDIR/run.json'"

ART="$ROOT/artifacts/$RUNID"
mkdir -p "$ART"
cp "$INSTR/submit.sbatch" "$ART/"
printf '%s\n' "$JOBID" > "$ART/jobid.txt"
echo "[S55] submitted runid=$RUNID jobid=$JOBID"
echo "[S55] poll: ssh $SSH sacct -j $JOBID --format=State,ExitCode,Elapsed -n"
