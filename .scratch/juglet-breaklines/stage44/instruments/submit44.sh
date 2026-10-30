#!/bin/bash
# ticket 44 -- render submit44.sbatch.tmpl, gate it, write the run directory, submit.
#
# Usage, from a directory holding the pushed commit's instruments (the submitter itself must
# come out of the commit, not off a laptop filesystem, so its line endings are the ones git
# stores):
#   bash submit44.sh <tag> <walltime>
# One phase (4): the ticket-44 formula cells for BOTH vessels (Juglet 1-9, Pot A 01-08, arms
# A today / B formula), thetas read from the COMMITTED thetas44.tsv, no partA dependency.
# The run directory shape and the four artefacts are the project convention:
#   /data/gpfs/projects/punim2657/SfSpp/runs/<YYYYMMDD-HHMM>_<git7>_t43-<tag>/
#       run.json  submit.sbatch  logs/  out/  instruments/
# instruments/ is a byte copy of the commit's stage44/instruments, because the job md5-compares
# what it executes against what the commit holds and fails rc=4 on any difference.
set -uo pipefail

TAG=${1:-}; WTIME=${2:-}
[ -n "$TAG" ] && [ -n "$WTIME" ] || {
  echo "usage: submit44.sh <tag> <walltime>" >&2; exit 2; }
PHASE=4
PARTA=committed

INSTR=$(cd "$(dirname "$0")" && pwd)
CANON=/data/gpfs/projects/punim2657/sfs_preprocessing
RUNS=/data/gpfs/projects/punim2657/SfSpp/runs
PY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3

# ---- the commit this job will build from: the branch head, which must be pushed already
git -C "$CANON" fetch --no-tags origin "+refs/heads/*:refs/remotes/origin/*" > /dev/null 2>&1
BRANCH=44-run-the-pipeline-at-the-curvature-derived-angle
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

for f in "$INSTR"/dist43.py "$INSTR"/mesh38.py "$INSTR"/measure34.py "$INSTR"/grow38.py \
         "$INSTR"/nest39.py "$INSTR"/wall40.py; do
  [ -f "$f" ] || { echo "missing instrument $f" >&2; exit 4; }
done
for f in "$INSTR"/run_cell44.sh "$INSTR"/thetas44.tsv "$INSTR"/spec44.tsv; do
  [ -f "$f" ] || { echo "missing instrument $f" >&2; exit 4; }
done
"$PY" -m py_compile "$INSTR"/*.py || { echo "py_compile failed" >&2; exit 4; }
find "$INSTR" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

# ---- the run directory
RUNID=$(date +%Y%m%d-%H%M)_"$GIT7"_t44-"$TAG"
RUN=$RUNS/$RUNID
[ -e "$RUN" ] && { echo "$RUN already exists" >&2; exit 5; }
mkdir -p "$RUN/logs" "$RUN/out" "$RUN/instruments"
for f in "$INSTR"/*.py "$INSTR"/*.sh "$INSTR"/*.tsv "$INSTR"/.gitattributes; do
  [ -f "$f" ] && cp -f "$f" "$RUN/instruments/";
done
cp -f "$INSTR"/submit44.sbatch.tmpl "$RUN/instruments/"

# ---- render
JOBNAME=t44-"$TAG"
"$PY" - "$INSTR/submit44.sbatch.tmpl" "$RUN/submit.sbatch" "$RUN" "$RUNID" "$NEW" "$PHASE" "$GIT7-t44-$TAG" "$WTIME" "$PARTA" "$JOBNAME" <<'PYEOF'
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
  "ticket": "44-run-the-pipeline-at-the-curvature-derived-angle",
  "runid": "$RUNID",
  "commit": "$NEW",
  "branch": "$BRANCH",
  "tag": "$GIT7-t44-$TAG",
  "phase": "$PHASE",
  "phase_meaning": "formula cells (A today / B ticket-43 k-rule theta), both vessels",
  "thetas_source": "committed stage44/instruments/thetas44.tsv, verbatim from ticket 43",
  "walltime": "$WTIME",
  "partition": "sapphire", "account": "punim2657", "cpus": 8, "mem": "64G",
  "instruments_md5": "$MD5",
  "instruments": sorted(__import__("os").listdir("$RUN/instruments")),
  "arms": {"A": "no env overrides (today)",
           "B": "SFS_PAPER_THETA=<ticket-43 k-rule theta: k x S/R_fold, k=3.3573>",
           "N": "no env overrides, second run -- the defaults-unchanged proof"},
  "proof_pieces": "Juglet:Juglet_Piece_2 Pot_A:Pot_A_Piece_01 Juglet:Juglet_Piece_5 Pot_A:Pot_A_Piece_07",
  "source_change": "none -- SFS_PAPER_THETA already exists (mesh_processing_headless.cpp:4574, gate at :3191)",
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
