#!/bin/bash
# ticket 42: render the sbatch script for one pot's job, prove the files are LF-only and
# parseable, and submit.  usage:
#   submit42.sh <rundir> <tag> <jobname> <walltime> <new_sha> <ref_sha> <phase 1|2> [--dry]
# one phase = one pot of the grid (1=Juglet nine sherds, 2=Pot A eight pieces), arms A/B of
# every piece plus R reference cells (arm A env on the pre-change binary) inside the SAME job.
set -uo pipefail

RUN=${1:-}; TAG=${2:-}; JOBNAME=${3:-}; WALL=${4:-}; SHA=${5:-}; REFSHA=${6:-}; PHASE=${7:-}; DRY=${8:-}
if [ -z "$RUN" ] || [ -z "$TAG" ] || [ -z "$JOBNAME" ] || [ -z "$WALL" ] || [ -z "$SHA" ] || [ -z "$REFSHA" ] || [ -z "$PHASE" ]; then
  echo "usage: submit42.sh <rundir> <tag> <jobname> <walltime> <new_sha> <ref_sha> <phase 1|2> [--dry]" >&2
  exit 2
fi
case "$PHASE" in
  1|2) ;;
  *) echo "[SUBMIT] FATAL ticket 42 has phases 1 (Juglet), 2 (Pot A); got '$PHASE'" >&2; exit 2 ;;
esac
for S in "$SHA" "$REFSHA"; do
  case "$S" in *[!0-9a-f]*) echo "[SUBMIT] FATAL sha is not lowercase hex: $S" >&2; exit 2 ;; esac
  [ "${#S}" -ge 40 ] || { echo "[SUBMIT] FATAL sha shorter than 40 chars: $S" >&2; exit 2; }
done
[ -d "$RUN" ] || { echo "[SUBMIT] FATAL no run dir $RUN" >&2; exit 2; }
TMPL=$RUN/instruments/submit42.sbatch.tmpl
[ -f "$TMPL" ] || { echo "[SUBMIT] FATAL no template $TMPL" >&2; exit 2; }
[ -f "$RUN/submit.sbatch" ] && { echo "[SUBMIT] FATAL $RUN/submit.sbatch already exists" >&2; exit 2; }
RUNID=$(basename "$RUN")
PY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3

if [ ! -f "$RUN/run.json" ]; then
  "$PY" - "$RUN/run.json" "$RUNID" "$TAG" "$SHA" "$REFSHA" "$PHASE" <<'PYEOF'
import json, sys, time
out, runid, tag, sha, refsha, phase = sys.argv[1:7]
POTS = {"1": ("Juglet", ["Juglet_Piece_%d" % i for i in range(1, 10)]),
        "2": ("Pot_A", ["Pot_A_Piece_%02d" % i for i in range(1, 9)])}
REFLIST = {"1": ["Juglet_Piece_1", "Juglet_Piece_3", "Juglet_Piece_5", "Juglet_Piece_7"],
           "2": ["Pot_A_Piece_07"]}
pot, pieces = POTS[phase]
rec = {"runid": runid, "tag": tag, "commit": sha, "ref_commit": refsha, "phase": phase, "pot": pot,
       "ticket": ".scratch/juglet-breaklines/issues/42-set-the-growth-angle-by-outcome.md",
       "question": "E4 - set the growth (smoothness) angle by the outcome, not as a shipped constant",
       "pieces": pieces,
       "arms": {"A": "today exactly: SFS_REASSIGN_MODE=radius SFS_MERGE_SCALE=literal + paper defaults",
                "B": "arm A + SFS_GROWTH_MODE=outcome (bidirectional paperTheta ladder 3.4,5.1,6.8,10.2,2.55,1.7,0.85 deg; largest theta with >=2 floor-clearing regions, else largest single region)",
                "R": "arm A env on the PRE-change binary (ref_commit) for the REFLIST pieces: proof 1 = identical SampledWithNormals md5 + identical [RETRY-23] sequences, A vs R"},
       "defaults": "SFS_PAPER_CHAIN=1 SFS_PAPER_THETA=3.4 SFS_PAPER_KAPPA=1.0 SFS_PAPER_NB=10 "
                   "SFS_SMOOTHNESS_DEG=3.4 SFS_CURVATURE_THRESH=1.0 SFS_REASSIGN_MODE=radius "
                   "SFS_MERGE_SCALE=literal; no SFS_DOWNSAMPLE_TARGET (pipeline downsamples itself); "
                   "SFS_GROWTH_MODE defaults to angle in the new binary (proof 2: zero ladder lines "
                   "in A/R logs, mode=angle in A/R, mode=outcome in B)",
       "ref_pieces": REFLIST[phase],
       "clouds": "real released .pcd clouds only, no synthetic",
       "controls": "arm-A surf-count anchors from ticket 41 recorded per cell (anchor_hit), not gated -- "
                   "the unseeded sampler's run-to-run spread is the standing tolerance",
       "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
json.dump(rec, open(out, "w"), indent=1, sort_keys=True)
PYEOF
  [ -f "$RUN/run.json" ] || { echo "[SUBMIT] FATAL could not write run.json" >&2; exit 2; }
fi

"$PY" - "$TMPL" "$RUN/submit.sbatch" "$RUN" "$RUNID" "$SHA" "$REFSHA" "$PHASE" "$JOBNAME" "$WALL" "$TAG" <<'PYEOF' || exit 3
import sys, re
tmpl, out, rundir, runid, sha, refsha, phase, jobname, wall, tag = sys.argv[1:11]
text = open(tmpl).read()
for k, v in (("__RUNDIR__", rundir), ("__RUNID__", runid), ("__NEWCOMMIT__", sha),
             ("__REFCOMMIT__", refsha), ("__PHASE__", phase), ("__JOBNAME__", jobname),
             ("__TIME__", wall), ("__IXTAG__", tag)):
    text = text.replace(k, v)
left = [t for t in ("__RUNDIR__", "__RUNID__", "__NEWCOMMIT__", "__REFCOMMIT__", "__PHASE__",
                    "__JOBNAME__", "__TIME__", "__IXTAG__") if t in text]
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
for s in run_cell42.sh stage_synth_p40.sh; do
  bash -n "$RUN/instruments/$s" || { echo "[SUBMIT] FATAL $s does not parse" >&2; exit 5; }
done
for p in wall40.py grow38.py nest39.py; do
  "$PY" -m py_compile "$RUN/instruments/$p" || { echo "[SUBMIT] FATAL $p does not compile" >&2; exit 5; }
done
echo "[SUBMIT] bash -n and py_compile clean"

{
  echo "runid=$RUNID tag=$TAG phase=$PHASE wall=$WALL"
  echo "commit=$SHA ref=$REFSHA"
  echo "jobname=$JOBNAME"
  ls -1 "$RUN"/instruments | tr '\n' ' '
  echo
} | tee -a "$RUN/logs/submit.log"

if [ "$DRY" = "--dry" ]; then
  echo "[SUBMIT] dry run, not submitting"
  exit 0
fi
cd "$RUN" && sbatch submit.sbatch | tee "$RUN/logs/sbatch.txt"
