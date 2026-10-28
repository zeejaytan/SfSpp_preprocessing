#!/bin/bash
# ticket 40: render the sbatch script for one group's job, prove the files are LF-only and
# parseable, and submit.  usage:
#   submit40.sh <rundir> <tag> <jobname> <walltime> <commit_sha> <phase 1|2|3> [--dry]
# one phase = one group of the grid (1=g1 synthetic Juglet, 2=g2 released Juglet, 3=g3 Pot A),
# both arms of every piece of the group inside the SAME job.  run.json is written on first use, so
# the run directory carries the parameters, the commit and the tag in its name.
set -uo pipefail

RUN=${1:-}; TAG=${2:-}; JOBNAME=${3:-}; WALL=${4:-}; SHA=${5:-}; PHASE=${6:-}; DRY=${7:-}
if [ -z "$RUN" ] || [ -z "$TAG" ] || [ -z "$JOBNAME" ] || [ -z "$WALL" ] || [ -z "$SHA" ] || [ -z "$PHASE" ]; then
  echo "usage: submit40.sh <rundir> <tag> <jobname> <walltime> <commit_sha> <phase 1|2|3> [--dry]" >&2
  exit 2
fi
for _p in $(echo "$PHASE" | tr ',' ' '); do
  case "$_p" in
    1|2|3) ;;
    *) echo "[SUBMIT] FATAL ticket 40 has phases 1, 2 and 3 (one per group); got '$PHASE'" >&2; exit 2 ;;
  esac
done
case "$PHASE" in *,*) PHASE_TAG=$(echo "$PHASE" | tr ',' '-') ;; *) PHASE_TAG=$PHASE ;; esac
case "$SHA" in *[!0-9a-f]*) echo "[SUBMIT] FATAL sha is not lowercase hex: $SHA" >&2; exit 2 ;; esac
[ "${#SHA}" -ge 40 ] || { echo "[SUBMIT] FATAL sha shorter than 40 chars: $SHA" >&2; exit 2; }
[ -d "$RUN" ] || { echo "[SUBMIT] FATAL no run dir $RUN" >&2; exit 2; }
TMPL=$RUN/instruments/submit40.sbatch.tmpl
[ -f "$TMPL" ] || { echo "[SUBMIT] FATAL no template $TMPL" >&2; exit 2; }
[ -f "$RUN/submit.sbatch" ] && { echo "[SUBMIT] FATAL $RUN/submit.sbatch already exists" >&2; exit 2; }
RUNID=$(basename "$RUN")
PY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3

if [ ! -f "$RUN/run.json" ]; then
  "$PY" - "$RUN/run.json" "$RUNID" "$TAG" "$SHA" "$PHASE" <<'PYEOF'
import json, sys, time
out, runid, tag, sha, phase = sys.argv[1:6]
GROUPS = {"1": "g1 synthetic Juglet, all nine sherds at own spacing, target pinned",
          "2": "g2 released Juglet .pcd clouds, no downsample override",
          "3": "g3 released Pot A .pcd clouds, no downsample override (regression control)"}
PIECES = {"1": ["Juglet_Piece_%d" % i for i in range(1, 10)],
          "2": ["Juglet_Piece_%d" % i for i in range(1, 10)],
          "3": ["Pot_A_Piece_%02d" % i for i in range(1, 9)]}
rec = {"runid": runid, "tag": tag, "commit": sha, "phase": phase, "group": GROUPS[phase],
       "ticket": ".scratch/juglet-breaklines/issues/40-is-own-mode-a-general-repair.md",
       "question": "U19 - is own mode a general repair, or a two-piece coincidence?",
       "pieces": PIECES[phase],
       "figures": ("F1 four views per piece both arms, F3 signed through histogram both arms, "
                   "F2 cross-piece shared fraction and mean dot (Pot A flagged)"),
       "arms": {"A": "SFS_REASSIGN_MODE=radius (shipped default, the control)",
                "B": "SFS_REASSIGN_MODE=own"},
       "defaults": "SFS_PAPER_CHAIN=1 SFS_PAPER_THETA=3.4 SFS_PAPER_KAPPA=1.0 SFS_PAPER_NB=10 "
                   "SFS_SMOOTHNESS_DEG=3.4 SFS_CURVATURE_THRESH=1.0, spacing policy unset (=piece); "
                   "g1 additionally pins SFS_DOWNSAMPLE_TARGET to its synthetic cloud's size, "
                   "g2/g3 set nothing (the pipeline downsamples itself, as shipped)",
       "controls": "g1 pieces 2 and 9 gate on ticket 39's own cloud and surface numbers before any "
                   "cell runs; g2/g3 anchor cells are recorded, not gated",
       "phases": {}, "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
json.dump(rec, open(out, "w"), indent=1, sort_keys=True)
PYEOF
  [ -f "$RUN/run.json" ] || { echo "[SUBMIT] FATAL could not write run.json" >&2; exit 2; }
fi

"$PY" - "$TMPL" "$RUN/submit.sbatch" "$RUN" "$RUNID" "$SHA" "$PHASE" "$JOBNAME" "$WALL" "$TAG" <<'PYEOF' || exit 3
import sys
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
open(out, "w", newline="\n").write(text)
print("[SUBMIT] rendered %s (%d bytes, phase %s)" % (out, len(text), phase))
PYEOF

# CRLF gate: a stray carriage return has already killed two grids on this project
CR=$(grep -lU $'\r' "$RUN/submit.sbatch" "$RUN"/instruments/*.py "$RUN"/instruments/*.sh \
      "$RUN"/instruments/*.txt "$RUN"/instruments/*.tmpl "$RUN/run.json" 2>/dev/null)
if [ -n "$CR" ]; then
  echo "[SUBMIT] FATAL carriage returns in:" >&2
  echo "$CR" >&2
  exit 4
fi
echo "[SUBMIT] CRLF gate clean"

bash -n "$RUN/submit.sbatch" || { echo "[SUBMIT] FATAL rendered script does not parse" >&2; exit 5; }
for s in run_cell40.sh run_fig40.sh stage_synth_p40.sh; do
  bash -n "$RUN/instruments/$s" || { echo "[SUBMIT] FATAL $s does not parse" >&2; exit 5; }
done
for p in wall40.py fig40.py; do
  "$PY" -m py_compile "$RUN/instruments/$p" || { echo "[SUBMIT] FATAL $p does not compile" >&2; exit 5; }
done
echo "[SUBMIT] bash -n and py_compile clean"

{
  echo "runid=$RUNID tag=$TAG phase=$PHASE wall=$WALL"
  echo "commit=$SHA"
  echo "jobname=$JOBNAME"
  ls -1 "$RUN"/instruments | tr '
' ' '
  echo
} | tee -a "$RUN/logs/submit.log"

if [ "$DRY" = "--dry" ]; then
  echo "[SUBMIT] dry run, not submitting"
  exit 0
fi
cd "$RUN" && sbatch submit.sbatch | tee "$RUN/logs/sbatch_phase$PHASE_TAG.txt"
