#!/bin/bash
# ticket 41: render the sbatch script for one pot's job, prove the files are LF-only and
# parseable, and submit.  usage:
#   submit41.sh <rundir> <tag> <jobname> <walltime> <commit_sha> <phase 1|2> [--dry]
# one phase = one pot of the grid (1=Juglet nine sherds, 2=Pot A eight pieces), all four arms of
# every piece inside the SAME job.  run.json is written on first use, so the run directory carries
# the parameters, the commit and the tag in its name.
set -uo pipefail

RUN=${1:-}; TAG=${2:-}; JOBNAME=${3:-}; WALL=${4:-}; SHA=${5:-}; PHASE=${6:-}; DRY=${7:-}
if [ -z "$RUN" ] || [ -z "$TAG" ] || [ -z "$JOBNAME" ] || [ -z "$WALL" ] || [ -z "$SHA" ] || [ -z "$PHASE" ]; then
  echo "usage: submit41.sh <rundir> <tag> <jobname> <walltime> <commit_sha> <phase 1|2> [--dry]" >&2
  exit 2
fi
case "$PHASE" in
  1|2|3) ;;
  *) echo "[SUBMIT] FATAL ticket 41 has phases 1 (Juglet), 2 (Pot A), 3 (measurement rerun); got '$PHASE'" >&2; exit 2 ;;
esac
case "$SHA" in *[!0-9a-f]*) echo "[SUBMIT] FATAL sha is not lowercase hex: $SHA" >&2; exit 2 ;; esac
[ "${#SHA}" -ge 40 ] || { echo "[SUBMIT] FATAL sha shorter than 40 chars: $SHA" >&2; exit 2; }
[ -d "$RUN" ] || { echo "[SUBMIT] FATAL no run dir $RUN" >&2; exit 2; }
TMPL=$RUN/instruments/submit41.sbatch.tmpl
[ -f "$TMPL" ] || { echo "[SUBMIT] FATAL no template $TMPL" >&2; exit 2; }
[ -f "$RUN/submit.sbatch" ] && { echo "[SUBMIT] FATAL $RUN/submit.sbatch already exists" >&2; exit 2; }
RUNID=$(basename "$RUN")
PY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3

if [ ! -f "$RUN/run.json" ]; then
  "$PY" - "$RUN/run.json" "$RUNID" "$TAG" "$SHA" "$PHASE" <<'PYEOF'
import json, sys, time
out, runid, tag, sha, phase = sys.argv[1:6]
POTS = {"1": ("Juglet", ["Juglet_Piece_%d" % i for i in range(1, 10)]),
        "2": ("Pot_A", ["Pot_A_Piece_%02d" % i for i in range(1, 9)]),
        "3": ("mixed", ["Juglet 1/5/7/8 arms ABC(+D on 1,7), Juglet 4/6 arm D, Pot A 01-08 all arms"])}
CELLS = {"3": "48 measurement cells: Juglet J1/J7 ABCD, J5/J8 ABC, J4/J6 D, Pot A 01-08 ABCD"}
pot, pieces = POTS[phase]
rec = {"runid": runid, "tag": tag, "commit": sha, "phase": phase, "pot": pot,
       "ticket": ".scratch/juglet-breaklines/issues/41-fix-pieces-4-6-and-default-own-mode.md",
       "question": "U19 - fix the pieces-4/6 loss under the adaptive default, then make own mode the default",
       "pieces": pieces,
       "arms": {"A": "SFS_REASSIGN_MODE=radius SFS_MERGE_SCALE=literal (today exactly; proof 1: explicit radius on the new binary reproduces ticket 40 g2/g3 arm A)",
                "B": "SFS_REASSIGN_MODE=own SFS_MERGE_SCALE=literal (the default-flip arm; proof 2 rides on the literal merge: same cluster counts as today on J1/J5/J7 and PA07)",
                "C": "SFS_REASSIGN_MODE=own SFS_MERGE_SCALE=spacing (rhoD scaled by S/0.6; the pieces-4/6 repair candidate)",
                "D": "SFS_REASSIGN_MODE=own SFS_MERGE_SCALE=literal SFS_SPACING_POLICY=fixed (the revert arm; pieces 4/6 must write two surfaces again)"},
       "defaults": "SFS_PAPER_CHAIN=1 SFS_PAPER_THETA=3.4 SFS_PAPER_KAPPA=1.0 SFS_PAPER_NB=10 "
                   "SFS_SMOOTHNESS_DEG=3.4 SFS_CURVATURE_THRESH=1.0, no SFS_DOWNSAMPLE_TARGET "
                   "(the pipeline downsamples itself, as shipped); the reassign-mode DEFAULT in the "
                   "binary itself is now own (ticket 41), so arm A pins radius explicitly",
       "clouds": "real released .pcd clouds only, no synthetic",
       "controls": "arm-A surf-count anchors from ticket 40 g2/g3 recorded per cell (anchor_hit), "
                   "not gated -- the unseeded sampler's run-to-run spread is the standing tolerance",
       "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
json.dump(rec, open(out, "w"), indent=1, sort_keys=True)
PYEOF
  [ -f "$RUN/run.json" ] || { echo "[SUBMIT] FATAL could not write run.json" >&2; exit 2; }
fi

"$PY" - "$TMPL" "$RUN/submit.sbatch" "$RUN" "$RUNID" "$SHA" "$PHASE" "$JOBNAME" "$WALL" "$TAG" <<'PYEOF' || exit 3
import sys, re
tmpl, out, rundir, runid, sha, phase, jobname, wall, tag = sys.argv[1:10]
text = open(tmpl).read()
for k, v in (("__RUNDIR__", rundir), ("__RUNID__", runid), ("__NEWCOMMIT__", sha),
             ("__PHASE__", phase), ("__JOBNAME__", jobname), ("__TIME__", wall),
             ("__IXTAG__", tag)):
    text = text.replace(k, v)
left = [t for t in ("__RUNDIR__", "__RUNID__", "__NEWCOMMIT__", "__PHASE__", "__JOBNAME__",
                    "__TIME__", "__IXTAG__") if t in text]
if left:
    raise SystemExit("[SUBMIT] FATAL unrendered placeholder(s): %s" % ", ".join(left))
# brace-stripping guard (trap 33875391): the rendered body must still hold its shell expansions
nexp = len(re.findall(r"[$][{]?[A-Za-z_][A-Za-z0-9_]*", text))
if nexp < 50:
    raise SystemExit("[SUBMIT] FATAL rendered script lost its shell expansions (%d found)" % nexp)
open(out, "w", newline="\n").write(text)
print("[SUBMIT] rendered %s (%d bytes, phase %s, %d shell expansions)" % (out, len(text), phase, nexp))
PYEOF

# CRLF gate: a stray carriage return has already killed two grids on this project
CR=$(grep -lU $'\r' "$RUN/submit.sbatch" $RUN/instruments/*.py $RUN/instruments/*.sh $RUN/instruments/*.tmpl "$RUN/run.json" 2>/dev/null)
if [ -n "$CR" ]; then
  echo "[SUBMIT] FATAL carriage returns in:" >&2
  echo "$CR" >&2
  exit 4
fi
echo "[SUBMIT] CRLF gate clean"

bash -n "$RUN/submit.sbatch" || { echo "[SUBMIT] FATAL rendered script does not parse" >&2; exit 5; }
for s in run_cell41.sh stage_synth_p40.sh; do
  bash -n "$RUN/instruments/$s" || { echo "[SUBMIT] FATAL $s does not parse" >&2; exit 5; }
done
for p in wall40.py grow38.py nest39.py mesh38.py measure34.py measure35.py; do
  "$PY" -m py_compile "$RUN/instruments/$p" || { echo "[SUBMIT] FATAL $p does not compile" >&2; exit 5; }
done
echo "[SUBMIT] bash -n and py_compile clean"

{
  echo "runid=$RUNID tag=$TAG phase=$PHASE wall=$WALL"
  echo "commit=$SHA"
  echo "jobname=$JOBNAME"
  ls -1 "$RUN"/instruments | tr '\n' ' '
  echo
} | tee -a "$RUN/logs/submit.log"

if [ "$DRY" = "--dry" ]; then
  echo "[SUBMIT] dry run, not submitting"
  exit 0
fi
cd "$RUN" && sbatch submit.sbatch | tee "$RUN/logs/sbatch.txt"
