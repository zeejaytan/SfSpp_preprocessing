#!/bin/bash
# ticket 42 measurement rerun -- render, VERIFY EVERY IMPORT, then submit ONE sbatch job.
# usage: submit_measure42.sh <rundir> <tag> <jobname> <walltime> <new_sha> <srcrun> [--dry]
# Runs on the login node from the run directory; instruments are copied into <rundir>/instruments.
set -uo pipefail

RUN=${1:-}; TAG=${2:-}; JOBNAME=${3:-}; WALL=${4:-}; SHA=${5:-}; SRCRUN=${6:-}; DRY=${7:-}
if [ -z "$RUN" ] || [ -z "$TAG" ] || [ -z "$JOBNAME" ] || [ -z "$WALL" ] || [ -z "$SHA" ] || [ -z "$SRCRUN" ]; then
  echo "usage: submit_measure42.sh <rundir> <tag> <jobname> <walltime> <new_sha> <srcrun> [--dry]" >&2
  exit 2
fi
case "$SHA" in *[!0-9a-f]*) echo "[SUBMIT] FATAL sha is not lowercase hex: $SHA" >&2; exit 2 ;; esac
[ "${#SHA}" -ge 40 ] || { echo "[SUBMIT] FATAL sha shorter than 40 chars" >&2; exit 2; }
[ -d "$RUN" ] || { echo "[SUBMIT] FATAL no run dir $RUN" >&2; exit 2; }
[ -d "$SRCRUN/out/cells-pipeline" ] || { echo "[SUBMIT] FATAL no cells-pipeline in $SRCRUN" >&2; exit 2; }
[ -f "$RUN/instruments/measure42.sbatch.tmpl" ] || { echo "[SUBMIT] FATAL no template in $RUN/instruments" >&2; exit 2; }
[ -f "$RUN/submit.sbatch" ] && { echo "[SUBMIT] FATAL $RUN/submit.sbatch already exists" >&2; exit 2; }
RUNID=$(basename "$RUN")
PY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3
INSTR=$RUN/instruments

# ---- CRLF gate first: a carriage return has killed two grids on this project
CR=$(grep -lU $'\r' "$INSTR"/*.py "$INSTR"/*.sh "$INSTR"/*.tmpl 2>/dev/null)
if [ -n "$CR" ]; then echo "[SUBMIT] FATAL carriage returns in:" >&2; echo "$CR" >&2; exit 4; fi
echo "[SUBMIT] CRLF gate clean"

# ---- parse + compile gates
bash -n "$INSTR/measure42.sh" || { echo "[SUBMIT] FATAL measure42.sh does not parse" >&2; exit 5; }
for p in grow38.py nest39.py replica37.py measure34.py mesh38.py; do
  "$PY" -m py_compile "$INSTR/$p" || { echo "[SUBMIT] FATAL $p does not compile" >&2; exit 5; }
done
echo "[SUBMIT] bash -n and py_compile clean"

# ---- VERIFY EVERY IMPORT with the exact python the job uses, before submit (ticket 41 died on
# replica37 ModuleNotFoundError; a compile pass does not prove an import)
( cd "$INSTR" && "$PY" -c "import replica37, measure34, mesh38, grow38, nest39; print('[IMPORTS] ok')" ) \
  || { echo "[SUBMIT] FATAL import check failed" >&2; exit 6; }
"$INSTR/../stage42/instruments/grow38.py" --help >/dev/null 2>&1 || true
( cd "$INSTR" && "$PY" grow38.py selftest > "$RUN/logs/selftest_grow38.log" 2>&1 ) \
  || { echo "[SUBMIT] FATAL grow38 selftest failed:" >&2; tail -5 "$RUN/logs/selftest_grow38.log" >&2; exit 6; }
( cd "$INSTR" && "$PY" nest39.py selftest > "$RUN/logs/selftest_nest39.log" 2>&1 ) \
  || { echo "[SUBMIT] FATAL nest39 selftest failed:" >&2; tail -5 "$RUN/logs/selftest_nest39.log" >&2; exit 6; }
echo "[SUBMIT] every import and selftest verified"

if [ ! -f "$RUN/run.json" ]; then
  "$PY" - "$RUN/run.json" "$RUNID" "$TAG" "$SHA" "$SRCRUN" <<'PYEOF'
import json, sys, time
out, runid, tag, sha, srcrun = sys.argv[1:6]
rec = {"runid": runid, "tag": tag, "commit": sha, "purpose": "measurement rerun",
       "source_run": srcrun, "source_jobid": "33959417",
       "ticket": ".scratch/juglet-breaklines/issues/42-set-the-growth-angle-by-outcome.md",
       "why": "the grid run of record completed its cells and kept 66 surface PLYs but died on "
              "ModuleNotFoundError replica37 before the measurement step, leaving surfaces.tsv, "
              "surface_pairs.tsv and nest.tsv header-only",
       "reads": "kept PLYs under source_run/out/cells-pipeline/*/surfaces/ + ORIGINAL released "
                "clouds/meshes; run of record and corpus are read-only (md5-proven in job)",
       "anchors": "J1 armA pair med_nn 2.0146 / med_along 1.8152 / med_across 0.5282 and "
                  "Pot_A PA01 armA 7.0952 / 7.0888 / 0.2709, +/-0.01, hard (miss -> exit 10)",
       "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
json.dump(rec, open(out, "w"), indent=1, sort_keys=True)
PYEOF
  [ -f "$RUN/run.json" ] || { echo "[SUBMIT] FATAL could not write run.json" >&2; exit 2; }
fi

"$PY" - "$INSTR/measure42.sbatch.tmpl" "$RUN/submit.sbatch" "$RUN" "$RUNID" "$SHA" "$SRCRUN" "$JOBNAME" "$WALL" "$TAG" <<'PYEOF' || exit 3
import sys, re
tmpl, out, rundir, runid, sha, srcrun, jobname, wall, tag = sys.argv[1:10]
text = open(tmpl).read()
for k, v in (("__RUNDIR__", rundir), ("__RUNID__", runid), ("__NEWCOMMIT__", sha),
             ("__SRCRUN__", srcrun), ("__JOBNAME__", jobname), ("__TIME__", wall),
             ("__IXTAG__", tag)):
    text = text.replace(k, v)
left = [t for t in ("__RUNDIR__", "__RUNID__", "__NEWCOMMIT__", "__SRCRUN__", "__JOBNAME__",
                    "__TIME__", "__IXTAG__") if t in text]
if left:
    raise SystemExit("[SUBMIT] FATAL unrendered placeholder(s): %s" % ", ".join(left))
nexp = len(re.findall(r"[$][{]?[A-Za-z_][A-Za-z0-9_]*", text))
if nexp < 50:
    raise SystemExit("[SUBMIT] FATAL rendered script lost its shell expansions (%d found)" % nexp)
open(out, "w", newline="\n").write(text)
print("[SUBMIT] rendered %s (%d bytes, %d shell expansions)" % (out, len(text), nexp))
PYEOF

CR=$(grep -lU $'\r' "$RUN/submit.sbatch" "$RUN/run.json" 2>/dev/null)
[ -n "$CR" ] && { echo "[SUBMIT] FATAL carriage returns in: $CR" >&2; exit 4; }
bash -n "$RUN/submit.sbatch" || { echo "[SUBMIT] FATAL rendered script does not parse" >&2; exit 5; }

{
  echo "runid=$RUNID tag=$TAG src=$SRCRUN wall=$WALL"
  echo "commit=$SHA"
  ls -1 "$INSTR" | tr '\n' ' '
  echo
} | tee -a "$RUN/logs/submit.log"

if [ "$DRY" = "--dry" ]; then
  echo "[SUBMIT] dry run, not submitting"
  exit 0
fi
cd "$RUN" && sbatch submit.sbatch | tee "$RUN/logs/sbatch.txt"
