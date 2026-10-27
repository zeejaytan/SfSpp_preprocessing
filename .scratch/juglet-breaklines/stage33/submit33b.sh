#!/usr/bin/env bash
# ticket 33, second submission: render submit.sbatch from submit33b.sbatch.tmpl and submit it.
# Runs ON Spartan, after <rundir>/instruments/ and <rundir>/run.json exist.
# Every placeholder the template carries is filled here; a leftover placeholder is a hard error,
# and a carriage return in any file the job will run is a hard error too (two grids in this
# project died on "set: pipefail: invalid option name").
# usage: submit33b.sh <rundir> <tag> <jobname> <walltime> <new_sha> <src1_out_dir>
#   src1_out_dir = the previous run's out/, which holds bin-orig, bin-new and cells/
set -uo pipefail
RUN=$1
TAG=$2
JOBNAME=$3
WTIME=$4
SHA=$5
SRC1=$6
SRC=$(cd "$(dirname "$0")" && pwd)
PY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3
TMPL=submit33b.sbatch.tmpl
RUNID=$(basename "$RUN")
if [ ! -d "$RUN" ]; then echo "[SUBMIT] FATAL no run dir $RUN"; exit 3; fi
if [ ! -f "$RUN/run.json" ]; then echo "[SUBMIT] FATAL no $RUN/run.json"; exit 3; fi
if [ ! -f "$SRC/$TMPL" ]; then echo "[SUBMIT] FATAL no template $SRC/$TMPL"; exit 3; fi
if [ -e "$RUN/submit.sbatch" ]; then echo "[SUBMIT] FATAL $RUN/submit.sbatch already exists"; exit 3; fi
case "$SHA" in
  *[!0-9a-f]*|"") echo "[SUBMIT] FATAL sha must be hex, got '$SHA'"; exit 3 ;;
esac
if [ "$#SHA}" -lt 40 ]; then echo "[SUBMIT] FATAL sha must be the full 40 characters, got '$#SHA}'"; exit 3; fi
for b in bin-orig bin-new; do
  if [ ! -x "$SRC1/$b" ]; then echo "[SUBMIT] FATAL $SRC1/$b missing -- this job reuses the previous run's binaries"; exit 3; fi
done
if [ ! -d "$SRC1/cells" ]; then echo "[SUBMIT] FATAL $SRC1/cells missing -- the previous run's cells are the comparison basis"; exit 3; fi
echo "[SUBMIT] runid=$RUNID new=$SHA tag=$TAG template=$TMPL time=$WTIME src1=$SRC1"
"$PY" - "$SRC/$TMPL" "$RUN/submit.sbatch" "$RUN" "$RUNID" "$SHA" "$WTIME" "$JOBNAME" "$TAG" "$SRC1" <<'PYEOF'
import pathlib, sys
tmpl, out, run, runid, sha, wtime, job, tag, src1 = sys.argv[1:10]
rep = {"__RUNDIR__": run, "__RUNID__": runid, "__NEWCOMMIT__": sha,
       "__IXTAG__": tag, "__JOBNAME__": job, "__TIME__": wtime, "__SRC1__": src1}
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
echo "[SUBMIT] no CRLF in submit.sbatch, instruments or run.json"
echo "[SUBMIT] instruments present: $(ls "$RUN"/instruments/*.py "$RUN"/instruments/*.sh | wc -l) files"
cd "$RUN" && sbatch submit.sbatch | tee logs/sbatch.txt
