#!/bin/bash
# ticket 39: render the sbatch script for the one job, prove the files are LF-only and parseable,
# and submit.  usage:
#   submit39.sh <rundir> <tag> <jobname> <walltime> <commit_sha> <phase 1|2> [--dry]
# run.json is written on first use, so the run directory carries the parameters, the commit and the
# tag in its name.
set -uo pipefail

RUN=${1:-}; TAG=${2:-}; JOBNAME=${3:-}; WALL=${4:-}; SHA=${5:-}; PHASE=${6:-}; DRY=${7:-}
if [ -z "$RUN" ] || [ -z "$TAG" ] || [ -z "$JOBNAME" ] || [ -z "$WALL" ] || [ -z "$SHA" ] || [ -z "$PHASE" ]; then
  echo "usage: submit39.sh <rundir> <tag> <jobname> <walltime> <commit_sha> <phase 1|2> [--dry]" >&2
  exit 2
fi
for _p in $(echo "$PHASE" | tr ',' ' '); do
  case "$_p" in
    1|2) ;;
    *) echo "[SUBMIT] FATAL ticket 39 has phases 1 and 2 only; got '$PHASE'" >&2; exit 2 ;;
  esac
done
case "$PHASE" in *,*) PHASE_TAG=$(echo "$PHASE" | tr ',' '-') ;; *) PHASE_TAG=$PHASE ;; esac
case "$SHA" in *[!0-9a-f]*) echo "[SUBMIT] FATAL sha is not lowercase hex: $SHA" >&2; exit 2 ;; esac
[ "${#SHA}" -ge 40 ] || { echo "[SUBMIT] FATAL sha shorter than 40 chars: $SHA" >&2; exit 2; }
[ -d "$RUN" ] || { echo "[SUBMIT] FATAL no run dir $RUN" >&2; exit 2; }
TMPL=$RUN/instruments/submit39.sbatch.tmpl
[ -f "$TMPL" ] || { echo "[SUBMIT] FATAL no template $TMPL" >&2; exit 2; }
[ -f "$RUN/submit.sbatch" ] && { echo "[SUBMIT] FATAL $RUN/submit.sbatch already exists" >&2; exit 2; }
RUNID=$(basename "$RUN")
PY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3

if [ ! -f "$RUN/run.json" ]; then
  "$PY" - "$RUN/run.json" "$RUNID" "$TAG" "$SHA" "$PHASE" <<'PYEOF'
import json, sys, time
out, runid, tag, sha, phase = sys.argv[1:6]
rec = {"runid": runid, "tag": tag, "commit": sha, "ticket":
       ".scratch/juglet-breaklines/issues/39-does-own-mode-keep-the-two-faces-apart.md",
       "question": "U19 - does SFS_REASSIGN_MODE=own keep the two faces apart?",
       "pieces": ["Juglet_Piece_9"] if phase == "2" else ["Juglet_Piece_2", "Juglet_Piece_9"],
       "figure": ("one edge-on plus three orthographic views per arm, and the signed through-distance "
                  "histogram of Surface_1 against Surface_0, from the surfaces these cells write"
                  if phase == "2" else ""),
       "arms": {"A": "SFS_REASSIGN_MODE=radius (shipped default, the control)",
                "B": "SFS_REASSIGN_MODE=own"},
       "defaults": "SFS_PAPER_CHAIN=1 SFS_PAPER_THETA=3.4 SFS_PAPER_KAPPA=1.0 SFS_PAPER_NB=10 "
                   "SFS_SMOOTHNESS_DEG=3.4 SFS_CURVATURE_THRESH=1.0, spacing policy unset (=piece), "
                   "no single-cluster write, no dedupe switch, no window override",
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
open(out, "w").write(text)
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
echo "[SUBMIT] bash -n clean"

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
cd "$RUN" && sbatch submit.sbatch | tee "$RUN/logs/sbatch_phase$PHASE_TAG.txt"
