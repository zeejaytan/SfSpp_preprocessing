#!/usr/bin/env bash
# ticket 32: render the run directory's submit.sbatch from the template beside this script
# and submit one job.  Runs ON Spartan, after <rundir>/instruments/ and <rundir>/run.json
# exist.  Every placeholder the template carries is filled here; a leftover placeholder is a
# hard error, and a carriage return in any file the job will run is a hard error too (two
# grids in this project died on "set: pipefail: invalid option name"; a CR in a list file
# would silently corrupt a cell name).
# usage: submit32.sh <rundir> <tag> <jobname> <walltime> <sha>
set -uo pipefail
RUN=$1
TAG=$2
JOBNAME=$3
WTIME=$4
SHA=$5
SRC=$(cd "$(dirname "$0")" && pwd)
PY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3
TMPL=submit32.sbatch.tmpl
RUNID=$(basename "$RUN")
if [ ! -d "$RUN" ]; then echo "[SUBMIT] FATAL no run dir $RUN"; exit 3; fi
if [ ! -f "$RUN/run.json" ]; then echo "[SUBMIT] FATAL no $RUN/run.json"; exit 3; fi
if [ ! -f "$SRC/$TMPL" ]; then echo "[SUBMIT] FATAL no template $SRC/$TMPL"; exit 3; fi
if [ -e "$RUN/submit.sbatch" ]; then echo "[SUBMIT] FATAL $RUN/submit.sbatch already exists"; exit 3; fi
case "$SHA" in
  *[!0-9a-f]*|"") echo "[SUBMIT] FATAL sha must be hex, got '$SHA'"; exit 3 ;;
esac
if [ "${#SHA}" -lt 40 ]; then echo "[SUBMIT] FATAL sha must be the full 40 characters, got '${#SHA}'"; exit 3; fi
echo "[SUBMIT] runid=$RUNID sha=$SHA tag=$TAG template=$TMPL time=$WTIME"
"$PY" - "$SRC/$TMPL" "$RUN/submit.sbatch" "$RUN" "$RUNID" "$SHA" "$WTIME" "$JOBNAME" "$TAG" <<'PYEOF'
import pathlib, sys
tmpl, out, run, runid, sha, wtime, job, tag = sys.argv[1:9]
rep = {"__RUNDIR__": run, "__RUNID__": runid, "__NEWCOMMIT__": sha,
       "__IXTAG__": tag, "__JOBNAME__": job, "__TIME__": wtime}
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
if grep -lU $'\r' "$RUN/submit.sbatch" "$RUN"/instruments/*.py "$RUN"/instruments/*.sh \
    "$RUN"/instruments/*.txt "$RUN"/run.json 2>/dev/null; then
  echo "[SUBMIT] FATAL CRLF in the files this job will run"; exit 4
fi
echo "[SUBMIT] no CRLF in submit.sbatch, instruments or list files"
echo "[SUBMIT] instruments present: $(ls "$RUN"/instruments/*.py "$RUN"/instruments/*.txt | wc -l) files"
cd "$RUN" && sbatch submit.sbatch | tee logs/sbatch.txt
