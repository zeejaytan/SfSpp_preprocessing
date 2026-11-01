#!/bin/bash
# ticket 54 -- render submit54.sbatch.tmpl, gate it, write the run directory, submit.
#
# Usage, from a directory holding the pushed commit's instruments (the submitter itself must
# come out of the commit, not off a laptop filesystem, so its line endings are the ones git
# stores):
#   bash submit54.sh <tag> <walltime>
# One phase (5): arms D (nothing set -- the shipped default), X (SFS_PAPER_THETA=3.4, the
# flat-theta control proving D is a no-op), W (SFS_WORNESS=0.9 -- the calibrated dial,
# expected to reproduce the t51/t52 capped thetas) and W7 (SFS_WORNESS=0.7 -- the dial
# turned down, thetas <= arm W) on all 17 pieces -- Juglet 1-9 on the ticket-47
# corpus-conforming clouds, Pot A 01-08 released clouds as the unchanged control --
# 68 cells + 2 FATAL probes (SFS_WORNESS=0 and =abc) in ONE job.
# Run directory: /data/gpfs/projects/punim2657/SfSpp/runs/<YYYYMMDD-HHMM>_<git7>_t54-<tag>/
set -uo pipefail

TAG=${1:-}; WTIME=${2:-}
[ -n "$TAG" ] && [ -n "$WTIME" ] || {
  echo "usage: submit54.sh <tag> <walltime>" >&2; exit 2; }
PHASE=5
PARTA=committed

INSTR=$(cd "$(dirname "$0")" && pwd)
CANON=/data/gpfs/projects/punim2657/sfs_preprocessing
RUNS=/data/gpfs/projects/punim2657/SfSpp/runs
PY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3

# ---- the commit this job will build from: the branch head, which must be pushed already
git -C "$CANON" fetch --no-tags origin "+refs/heads/*:refs/remotes/origin/*" > /dev/null 2>&1
BRANCH=54-rename-the-worn-edge-cap-to-worness-a-dial
NEW=$(git -C "$CANON" rev-parse "refs/remotes/origin/$BRANCH" 2>/dev/null)
[ -n "$NEW" ] || { echo "cannot resolve origin/$BRANCH in $CANON" >&2; exit 3; }
LOCAL=$(git -C "$INSTR" rev-parse HEAD 2>/dev/null || echo none)
if [ "$LOCAL" != "none" ] && [ "$LOCAL" != "$NEW" ]; then
  echo "WARN the submitter came from $LOCAL but origin/$BRANCH is $NEW" >&2
fi
GIT7=$(printf %s "$NEW" | cut -c1-7)

# ---- the line-ending gate, before anything else is written
bad=0
for f in "$INSTR"/*.sh "$INSTR"/*.py "$INSTR"/*.tmpl "$INSTR"/*.tsv; do
  [ -f "$f" ] || continue
  if grep -qU $'\r' "$f" 2>/dev/null; then echo "CRLF in $f" >&2; bad=1; fi
done
[ "$bad" -eq 0 ] || { echo "refusing to submit: CRLF above kills bash (pipefail)" >&2; exit 4; }

for f in "$INSTR"/run_cell54.sh "$INSTR"/stage_synth_p40.sh; do
  [ -f "$f" ] || { echo "missing instrument $f" >&2; exit 4; }
done
"$PY" -m py_compile "$INSTR"/*.py || { echo "py_compile failed" >&2; exit 4; }
find "$INSTR" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

# ---- the run directory
RUNID=$(date +%Y%m%d-%H%M)_"$GIT7"_t54-"$TAG"
RUN=$RUNS/$RUNID
[ -e "$RUN" ] && { echo "$RUN already exists" >&2; exit 5; }
mkdir -p "$RUN/logs" "$RUN/out" "$RUN/instruments"
for f in "$INSTR"/*.py "$INSTR"/*.sh "$INSTR"/*.tsv "$INSTR"/.gitattributes; do
  [ -f "$f" ] && cp -f "$f" "$RUN/instruments/"
done
cp -f "$INSTR"/submit54.sbatch.tmpl "$RUN/instruments/"

# ---- render
JOBNAME=t54-"$TAG"
"$PY" - "$INSTR/submit54.sbatch.tmpl" "$RUN/submit.sbatch" "$RUN" "$RUNID" "$NEW" "$PHASE" "$GIT7-t54-$TAG" "$WTIME" "$PARTA" "$JOBNAME" <<'PYEOF'
import sys
tmpl, dst, rundir, runid, new, phase, ixtag, wtime, parta, jobname = sys.argv[1:11]
text = open(tmpl, "r", encoding="utf-8", newline="").read()
if "\r" in text:
    sys.exit("template has CRLF")
subs = {"__JOBNAME__": jobname, "__RUNDIR__": rundir, "__RUNID__": runid,
    "__NEWCOMMIT__": new, "__PHASE__": phase, "__IXTAG__": ixtag,
    "__TIME__": wtime, "__PARTA__": parta}
for k, v in subs.items():
    text = text.replace(k, v)
open(dst, "w", encoding="utf-8", newline="\n").write(text)
PYEOF
[ $? -eq 0 ] || { echo "render failed" >&2; exit 6; }

# ---- the gates: no placeholder survives, the script parses, and it still has its expansions
if grep -n "__[A-Z][A-Z]*__" "$RUN/submit.sbatch"; then
  echo "unrendered placeholder above -- the template grew a field the renderer does not fill" >&2
  exit 6
fi
bash -n "$RUN/submit.sbatch" || { echo "submit.sbatch does not parse" >&2; exit 6; }
NEXP=$(grep -o '\$[A-Za-z_][A-Za-z0-9_]*' "$RUN/submit.sbatch" | wc -l)
if [ "$NEXP" -lt 40 ]; then
  echo "only $NEXP shell expansions survived rendering (expected >=40) -- braces were eaten" >&2
  exit 6
fi
if grep -qU $'\r' "$RUN/submit.sbatch"; then echo "rendered submit.sbatch has CRLF" >&2; exit 6; fi
echo "[SUBMIT] rendered $RUN/submit.sbatch ($NEXP expansions, $(wc -l < "$RUN/submit.sbatch") lines)"

MD5=$(cd "$RUN/instruments" && md5sum *.py *.sh *.tsv 2>/dev/null | sort -k2 | md5sum | cut -d' ' -f1)
"$PY" - "$RUN/run.json" <<PYEOF
import json, sys
json.dump({
  "ticket": "54-rename-the-worn-edge-cap-to-worness-a-dial",
  "part": "1 of 1",
  "runid": "$RUNID",
  "commit": "$NEW",
  "branch": "$BRANCH",
  "tag": "$GIT7-t54-$TAG",
  "phase": "$PHASE",
  "phase_meaning": "arms D (nothing set, shipped default), X (SFS_PAPER_THETA=3.4 flat-theta control), W (SFS_WORNESS=0.9 calibrated dial) and W7 (SFS_WORNESS=0.7) on 17 pieces = 68 cells + 2 FATAL probes in one job",
  "walltime": "$WTIME",
  "partition": "sapphire", "account": "punim2657", "cpus": 8, "mem": "64G",
  "instruments_md5": "$MD5",
  "instruments": sorted(__import__("os").listdir("$RUN/instruments")),
  "arms": {"D": "nothing set -- the shipped default (flat theta 3.4); no [GROWTH-45]/[WORNESS-54]/[GROWTH-51] line; the no-op baseline arm X must match",
           "X": "SFS_PAPER_THETA=3.4 -- the explicit flat-theta control; D must match it on thetas + surface point counts (mesh stage unseeded, bytes never compared)",
           "W": "SFS_WORNESS=0.9 -- the calibrated dial: formula theta AND cap 0.9*crossing ([GROWTH-45] then [WORNESS-54]); expected to reproduce the t51/t52 capped thetas",
           "W7": "SFS_WORNESS=0.7 -- the dial turned down; thetas must be <= arm W's on every piece"},
  "fatal_probes": "SFS_WORNESS=0 and SFS_WORNESS=abc on Juglet_Piece_1: rc != 0 + the [WORNESS-54] FATAL line + no surface grown (run_cell54.sh pass F)",
  "corpus_gate": "pass 1 of run_cell54.sh: md5 AND kept_points of every Juglet corpus cloud must equal MANIFEST_JUGLET_CC.tsv (columns by header name) and no *_covering.pcd may sit under the corpus Point trees; Pot A released clouds recorded, not gated",
  "env_proof": "POSITIVE apptainer env probe per cell (same container, same env-prefix as the pipeline invocation): D exactly empty, X exactly SFS_PAPER_THETA=3.4, W exactly SFS_WORNESS=0.9, W7 exactly SFS_WORNESS=0.7",
  "source_change": "mesh_processing_headless.cpp: SFS_WORNESS (getenv + strtod, errno/endptr guarded). Unset/empty = OFF. 0 < w <= 1 enters the formula path and caps theta at w*thetaCross51 (the t51 0.9 promoted to a dial); anything else FATAL '[WORNESS-54] FATAL SFS_WORNESS=...' exit 2. Precedence SFS_PAPER_THETA > SFS_WORNESS > SFS_GROWTH_FORMULA/CAP (both unchanged).",
}, open(sys.argv[1], "w"), indent=2, sort_keys=True)
PYEOF

cd "$RUN" || exit 7
JOB=$(sbatch --parsable "$RUN/submit.sbatch" 2>&1)
echo "[SUBMIT] sbatch said: $JOB"
case "$JOB" in
  *[!0-9]*) echo "[SUBMIT] sbatch did not return a job id -- the run directory stays for inspection: $RUN" >&2; exit 8 ;;
esac
echo "$JOB" > "$RUN/logs/jobid.txt"
echo "[SUBMIT] run=$RUN"
echo "[SUBMIT] jobid=$JOB"
squeue -j "$JOB" -o "%.18i %.9P %.30j %.8T %.10M %.6D %R" || true
