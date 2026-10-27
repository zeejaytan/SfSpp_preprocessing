#!/usr/bin/env bash
# ticket 32 fixup: render the run directory's submit.sbatch from submitFIX.sbatch.tmpl beside
# this script and submit one job.  Runs ON Spartan, after <rundir>/instruments/ and
# <rundir>/run.json exist.  Same gates as submit32.sh: every placeholder must be filled, and a
# carriage return in any file the job will run is a hard error.
# usage: submitFIX32.sh <rundir> <tag> <jobname> <walltime> <sha> <srcrunid>
set -uo pipefail
RUN=$1
TAG=$2
JOBNAME=$3
WTIME=$4
SHA=$5
SRCRUNID=$6
SRC=$(cd "$(dirname "$0")" && pwd)
PY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3
TMPL=submitFIX.sbatch.tmpl
RUNID=$(basename "$RUN")
if [ ! -d "$RUN" ]; then echo "[SUBMIT] FATAL no run dir $RUN"; exit 3; fi
if [ ! -f "$RUN/run.json" ]; then echo "[SUBMIT] FATAL no $RUN/run.json"; exit 3; fi
if [ ! -f "$SRC/$TMPL" ]; then echo "[SUBMIT] FATAL no template $SRC/$TMPL"; exit 3; fi
if [ -e "$RUN/submit.sbatch" ]; then echo "[SUBMIT] FATAL $RUN/submit.sbatch already exists"; exit 3; fi
if [ ! -d "/data/gpfs/projects/punim2657/SfSpp/runs/$SRCRUNID/out/cells" ]; then
  echo "[SUBMIT] FATAL no source cells under runs/$SRCRUNID/out/cells"; exit 3
fi
case "$SHA" in
  *[!0-9a-f]*|"") echo "[SUBMIT] FATAL sha must be hex, got '$SHA'"; exit 3 ;;
esac
if [ "${#SHA}" -lt 40 ]; then echo "[SUBMIT] FATAL sha must be the full 40 characters, got '${#SHA}'"; exit 3; fi
echo "[SUBMIT] runid=$RUNID sha=$SHA tag=$TAG template=$TMPL time=$WTIME source=$SRCRUNID"
"$PY" - "$SRC/$TMPL" "$RUN/submit.sbatch" "$RUN" "$RUNID" "$SHA" "$WTIME" "$JOBNAME" "$TAG" "$SRCRUNID" <<'PYEOF'
import pathlib, sys
tmpl, out, run, runid, sha, wtime, job, tag, srcrun = sys.argv[1:10]
rep = {"__RUNDIR__": run, "__RUNID__": runid, "__NEWCOMMIT__": sha,
       "__IXTAG__": tag, "__JOBNAME__": job, "__TIME__": wtime, "__SRCRUN__": srcrun}
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
    "$RUN"/instruments/*.tmpl "$RUN"/run.json 2>/dev/null; then
  echo "[SUBMIT] FATAL CRLF in the files this job will run"; exit 4
fi
echo "[SUBMIT] no CRLF in submit.sbatch, instruments or run.json"
cd "$RUN" && sbatch submit.sbatch | tee logs/sbatch.txt
