#!/bin/bash
# ticket 46 -- render submit46.sbatch.tmpl, gate it, write the run directory, submit.
#
# Usage, from a directory holding the pushed commit's instruments (the submitter itself must
# come out of the commit, not off a laptop filesystem, so its line endings are the ones git
# stores):
#   bash submit46.sh <tag> <walltime>
# One job, five phases in order (PHASE=all): introduce the even covering of each Juglet piece
# (phase 1), run the 17 cells with no SFS_* env anywhere (phase 4), compare the thetas with
# ticket 43's k-rule and ticket 45's measurement (phase 7), measure the pairs of whatever grew
# two surfaces (phase 8), draw the two pictures (phase 9).  No source change: the binary is built
# from the branch head, which carries ticket 45's commits.
# The run directory shape and the artefacts are the project convention:
#   /data/gpfs/projects/punim2657/SfSpp/runs/<YYYYMMDD-HHMM>_<git7>_t46-<tag>/
#       run.json  submit.sbatch  logs/  out/  instruments/
# instruments/ is a byte copy of the commit's stage46/instruments, because the job md5-compares
# what it executes against what the commit holds and fails rc=4 on any difference.
set -uo pipefail

TAG=${1:-}; WTIME=${2:-}
[ -n "$TAG" ] && [ -n "$WTIME" ] || {
  echo "usage: submit46.sh <tag> <walltime>" >&2; exit 2; }
PHASE=all
PARTA=committed

INSTR=$(cd "$(dirname "$0")" && pwd)
CANON=/data/gpfs/projects/punim2657/sfs_preprocessing
RUNS=/data/gpfs/projects/punim2657/SfSpp/runs
PY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3

# ---- the commit this job will build from: the branch head, which must be pushed already
git -C "$CANON" fetch --no-tags origin "+refs/heads/*:refs/remotes/origin/*" > /dev/null 2>&1
BRANCH=46-feed-the-growth-an-even-covering
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

for f in "$INSTR"/run_cell46.sh "$INSTR"/stage_synth_p40.sh "$INSTR"/spec46.tsv \
         "$INSTR"/cover_cloud46.py "$INSTR"/theta_check46.py "$INSTR"/run_measure34.py "$INSTR"/figures46.py; do
  [ -f "$f" ] || { echo "missing instrument $f" >&2; exit 4; }
done
"$PY" -m py_compile "$INSTR"/*.py || { echo "py_compile failed" >&2; exit 4; }
find "$INSTR" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

# ---- the run directory
RUNID=$(date +%Y%m%d-%H%M)_"$GIT7"_t46-"$TAG"
RUN=$RUNS/$RUNID
[ -e "$RUN" ] && { echo "$RUN already exists" >&2; exit 5; }
mkdir -p "$RUN/logs" "$RUN/out" "$RUN/instruments"
for f in "$INSTR"/*.py "$INSTR"/*.sh "$INSTR"/*.tsv "$INSTR"/.gitattributes; do
  [ -f "$f" ] && cp -f "$f" "$RUN/instruments/";
done
cp -f "$INSTR"/submit46.sbatch.tmpl "$RUN/instruments/"

# ---- render
JOBNAME=t46-"$TAG"
"$PY" - "$INSTR/submit46.sbatch.tmpl" "$RUN/submit.sbatch" "$RUN" "$RUNID" "$NEW" "$PHASE" "$GIT7-t46-$TAG" "$WTIME" "$PARTA" "$JOBNAME" <<'PYEOF'
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
  "ticket": "46-feed-the-growth-an-even-covering",
  "runid": "$RUNID",
  "commit": "$NEW",
  "branch": "$BRANCH",
  "tag": "$GIT7-t46-$TAG",
  "phase": "$PHASE",
  "phase_meaning": "1 = even covering of each Juglet piece from its own shipped mesh at the spacing the run already resolves; 4 = 9 Juglet cells on the covering (arm E) + 8 Pot A cells on their released clouds (arm A), no SFS_* env in any cell; 7 = theta against ticket 43 k-rule (2 pct) and ticket 45 arm F; 8 = measure34 pair table; 9 = two figures",
  "source_change": "none -- the binary is built from the branch head (ticket 45 commits included) and every cell runs the no-env default path",
  "method_note": "NOT the paper method: the paper resamples the BREAKLINE at 1.9 mm (ticket 06); this run covers the shipped MESH at the piece spacing S from spec46.tsv, which is a diagnostic of the measurement, not a claim of the paper pipeline",
  "walltime": "$WTIME",
  "partition": "sapphire", "account": "punim2657", "cpus": 8, "mem": "64G",
  "instruments_md5": "$MD5",
  "instruments": sorted(__import__("os").listdir("$RUN/instruments")),
  "arms": {"E": "covering -- the cell reads an even covering of the piece own shipped mesh (S per piece from spec46.tsv), no env",
           "A": "control-released -- the Pot A cell reads its released cloud exactly as ticket 45 arm F did, no env"},
  "proof": "per-cell env_proof.tsv (every theta_env must read <none>) and spacing_proof.tsv (S must equal spec46 within 1e-3 mm)",
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
