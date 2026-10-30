#!/bin/bash
# ticket 45 -- render submit45.sbatch.tmpl, gate it, write the run directory, submit.
#
# Usage, from a directory holding the pushed commit's instruments (the submitter itself must
# come out of the commit, not off a laptop filesystem, so its line endings are the ones git
# stores):
#   bash submit45.sh <tag> <walltime>
# One phase (4): arm F (no env -- the NEW curvature-derived default theta) on all 17 pieces
# (Juglet 1-9, Pot A 01-08), plus arm O (SFS_PAPER_THETA=3.4, today's path) on the four proof
# pieces, thetas44.tsv committed as the REFERENCE only.
# The run directory shape and the artefacts are the project convention:
#   /data/gpfs/projects/punim2657/SfSpp/runs/<YYYYMMDD-HHMM>_<git7>_t45-<tag>/
#       run.json  submit.sbatch  logs/  out/  instruments/
# instruments/ is a byte copy of the commit's stage45/instruments, because the job md5-compares
# what it executes against what the commit holds and fails rc=4 on any difference.
set -uo pipefail

TAG=${1:-}; WTIME=${2:-}
[ -n "$TAG" ] && [ -n "$WTIME" ] || {
  echo "usage: submit45.sh <tag> <walltime>" >&2; exit 2; }
PHASE=4
PARTA=committed

INSTR=$(cd "$(dirname "$0")" && pwd)
CANON=/data/gpfs/projects/punim2657/sfs_preprocessing
RUNS=/data/gpfs/projects/punim2657/SfSpp/runs
PY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3

# ---- the commit this job will build from: the branch head, which must be pushed already
git -C "$CANON" fetch --no-tags origin "+refs/heads/*:refs/remotes/origin/*" > /dev/null 2>&1
BRANCH=45-adopt-the-curvature-formula-as-the-default-growth-angle
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

for f in "$INSTR"/run_cell45.sh "$INSTR"/stage_synth_p40.sh "$INSTR"/thetas44.tsv; do
  [ -f "$f" ] || { echo "missing instrument $f" >&2; exit 4; }
done
"$PY" -m py_compile "$INSTR"/*.py || { echo "py_compile failed" >&2; exit 4; }
find "$INSTR" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

# ---- the run directory
RUNID=$(date +%Y%m%d-%H%M)_"$GIT7"_t45-"$TAG"
RUN=$RUNS/$RUNID
[ -e "$RUN" ] && { echo "$RUN already exists" >&2; exit 5; }
mkdir -p "$RUN/logs" "$RUN/out" "$RUN/instruments"
for f in "$INSTR"/*.py "$INSTR"/*.sh "$INSTR"/*.tsv "$INSTR"/.gitattributes; do
  [ -f "$f" ] && cp -f "$f" "$RUN/instruments/";
done
cp -f "$INSTR"/submit45.sbatch.tmpl "$RUN/instruments/"

# ---- render
JOBNAME=t45-"$TAG"
"$PY" - "$INSTR/submit45.sbatch.tmpl" "$RUN/submit.sbatch" "$RUN" "$RUNID" "$NEW" "$PHASE" "$GIT7-t45-$TAG" "$WTIME" "$PARTA" "$JOBNAME" <<'PYEOF'
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
  "ticket": "45-adopt-the-curvature-formula-as-the-default-growth-angle",
  "runid": "$RUNID",
  "commit": "$NEW",
  "branch": "$BRANCH",
  "tag": "$GIT7-t45-$TAG",
  "phase": "$PHASE",
  "phase_meaning": "arm F no-env (the new curvature-derived default theta) on 17 pieces, arm O SFS_PAPER_THETA=3.4 (today's path) on the 4 proof pieces",
  "thetas_source": "committed stage45/instruments/thetas44.tsv, REFERENCE ONLY (ticket 43 k-rule table; no cell reads it)",
  "walltime": "$WTIME",
  "partition": "sapphire", "account": "punim2657", "cpus": 8, "mem": "64G",
  "instruments_md5": "$MD5",
  "instruments": sorted(__import__("os").listdir("$RUN/instruments")),
  "arms": {"F": "no env overrides -- the new default computes theta = 3.3573 x S/R_fold x 180/pi (logged [GROWTH-45])",
           "O": "SFS_PAPER_THETA=3.4 -- today's path, byte-for-byte (the override proof)"},
  "proof_pieces": "Juglet:Juglet_Piece_2 Pot_A:Pot_A_Piece_01 Juglet:Juglet_Piece_5 Pot_A:Pot_A_Piece_07",
  "source_change": "mesh_processing_headless.cpp: medianFoldRadius45() + the ticket-45 caller block -- with SFS_PAPER_THETA unset theta comes from the piece's own curvature; env set keeps today's behaviour; SFS_GROWTH_MODE=outcome ladder untouched",
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
