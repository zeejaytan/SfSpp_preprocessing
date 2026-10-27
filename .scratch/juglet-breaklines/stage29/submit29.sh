#!/usr/bin/env bash
# ticket 29: render the run directory's submit.sbatch from the template beside this
# script and submit one job. Runs ON Spartan, after <rundir>/instruments/ is populated.
# usage: submit29.sh <rundir> <tag> <jobname> <walltime> <sha>
set -uo pipefail
RUN=$1
TAG=$2
JOBNAME=$3
WTIME=$4
SHA=$5
SRC=$(cd "$(dirname "$0")" && pwd)
PY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3
ROOT=/data/gpfs/projects/punim2657/SfSpp/runs
GRID=$ROOT/20261027-0337_d69f76f_t25-dump-grid2/out/dump
POTA=$ROOT/20261027-1537_5227f8f_t28-pota07-dump/out/dump
RUNID=$(basename "$RUN")
if [ ! -d "$RUN" ]; then echo "[SUBMIT] FATAL no run dir $RUN"; exit 3; fi
if [ ! -d "$GRID" ]; then echo "[SUBMIT] FATAL borrowed grid dump missing $GRID"; exit 3; fi
if [ ! -d "$POTA" ]; then echo "[SUBMIT] FATAL borrowed Pot A dump missing $POTA"; exit 3; fi
if [ -e "$RUN/submit.sbatch" ]; then echo "[SUBMIT] FATAL $RUN/submit.sbatch already exists"; exit 3; fi
echo "[SUBMIT] runid=$RUNID sha=$SHA tag=$TAG"
"$PY" - "$SRC/submit_29_survey.sbatch" "$RUN/submit.sbatch" "$RUN" "$RUNID" "$SHA" "$WTIME" "$JOBNAME" "$TAG" "$GRID" "$POTA" <<'PYEOF'
import pathlib, sys
tmpl, out, run, runid, sha, wtime, job, tag, grid, pota = sys.argv[1:11]
rep = {"__RUNDIR__": run, "__RUNID__": runid, "__NEWCOMMIT__": sha,
       "__IXTAG__": tag, "__JOBNAME__": job, "__TIME__": wtime,
       "__GRIDROOT__": grid, "__POTAROOT__": pota}
t = pathlib.Path(tmpl).read_text()
for k, v in rep.items():
    t = t.replace(k, v)
left = sorted(p for p in rep if p in t)
if left:
    raise SystemExit("[SUBMIT] unfilled placeholders: %r" % left)
pathlib.Path(out).write_text(t)
print("[SUBMIT] wrote", out, len(t), "bytes")
PYEOF
if grep -lU $'\r' "$RUN/submit.sbatch" "$RUN/instruments"/*.py "$RUN/instruments"/*.sh 2>/dev/null; then
  echo "[SUBMIT] FATAL CRLF in the files this job will run"; exit 4
fi
echo "[SUBMIT] no CRLF in submit.sbatch or instruments"
cd "$RUN" && sbatch submit.sbatch | tee logs/sbatch.txt
