#!/usr/bin/env bash
# ticket 30: render a run directory's submit.sbatch from a template beside this script and
# submit one job. Runs ON Spartan, after <rundir>/instruments/ and <rundir>/run.json exist.
# usage: submit30.sh <rundir> <tag> <jobname> <walltime> <sha> <template>
#        env: THETA (arm jobs only), PIECES (arm jobs only), ROLE (arm jobs only)
# Every placeholder the template carries is filled here; any left over is a hard error, and a
# carriage return in any file the job will run is a hard error too (two grids died on
# "set: pipefail: invalid option name").
set -uo pipefail
RUN=$1
TAG=$2
JOBNAME=$3
WTIME=$4
SHA=$5
TMPL=$6
SRC=$(cd "$(dirname "$0")" && pwd)
PY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3
THETA=${THETA:-}
PIECES=${PIECES:-}
ROLE=${ROLE:-test}
RUNID=$(basename "$RUN")
if [ ! -d "$RUN" ]; then echo "[SUBMIT] FATAL no run dir $RUN"; exit 3; fi
if [ ! -f "$RUN/run.json" ]; then echo "[SUBMIT] FATAL no $RUN/run.json"; exit 3; fi
if [ ! -f "$SRC/$TMPL" ]; then echo "[SUBMIT] FATAL no template $SRC/$TMPL"; exit 3; fi
if [ -e "$RUN/submit.sbatch" ]; then echo "[SUBMIT] FATAL $RUN/submit.sbatch already exists"; exit 3; fi
if grep -q "__THETA__" "$SRC/$TMPL"; then
  case "$THETA" in ""|*[!0-9.]*) echo "[SUBMIT] FATAL THETA must be a decimal number, got '$THETA'"; exit 3 ;; esac
  if ! "$PY" -c "import sys; float(sys.argv[1])" "$THETA" 2>/dev/null; then
    echo "[SUBMIT] FATAL THETA not a number: $THETA"; exit 3
  fi
fi
if grep -q "__PIECES__" "$SRC/$TMPL" && [ -z "$PIECES" ]; then
  echo "[SUBMIT] FATAL template wants PIECES and none were given"; exit 3
fi
echo "[SUBMIT] runid=$RUNID sha=$SHA tag=$TAG template=$TMPL theta=${THETA:-none} pieces=$(echo $PIECES | wc -w) role=$ROLE"
"$PY" - "$SRC/$TMPL" "$RUN/submit.sbatch" "$RUN" "$RUNID" "$SHA" "$WTIME" "$JOBNAME" "$TAG" "$THETA" "$PIECES" "$ROLE" <<'PYEOF'
import pathlib, sys
tmpl, out, run, runid, sha, wtime, job, tag, theta, pieces, role = sys.argv[1:12]
rep = {"__RUNDIR__": run, "__RUNID__": runid, "__NEWCOMMIT__": sha,
       "__IXTAG__": tag, "__JOBNAME__": job, "__TIME__": wtime,
       "__THETA__": theta, "__PIECES__": pieces, "__ROLE__": role}
t = pathlib.Path(tmpl).read_text()
for k, v in rep.items():
    t = t.replace(k, v)
left = sorted(p for p in rep if p in t)
if left:
    raise SystemExit("[SUBMIT] unfilled placeholders: %r" % left)
pathlib.Path(out).write_text(t)
print("[SUBMIT] wrote", out, len(t), "bytes")
PYEOF
RC=$?
[ "$RC" -eq 0 ] || exit "$RC"
if grep -lU $'\r' "$RUN/submit.sbatch" "$RUN/instruments"/*.py "$RUN/instruments"/*.sh 2>/dev/null; then
  echo "[SUBMIT] FATAL CRLF in the files this job will run"; exit 4
fi
echo "[SUBMIT] no CRLF in submit.sbatch or instruments"
cd "$RUN" && sbatch submit.sbatch | tee logs/sbatch.txt
