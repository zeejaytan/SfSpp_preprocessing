#!/bin/bash
# submit47.sh <tag> [walltime] -- ticket 47 run submitter (Spartan login node).
#
# Mirrors the t45/t46 submit-from-pushed-commit pattern: the canonical checkout
# fetches (never edits), the instruments are byte-frozen out of the pushed commit
# via git archive, the template is rendered with a plain python replace, gated
# (CRLF, py_compile, no unrendered placeholder, bash -n, expansion count), and
# only then sbatch'd.  The job re-verifies its instruments against the same
# commit on the compute node (phase 0), so what ran is what was pushed.
#
# usage: bash submit47.sh jugletcc 00:30:00
set -euo pipefail

TAG=$1
[ -n "$TAG" ] || TAG=jugletcc
WALL=$2
[ -n "$WALL" ] || WALL=00:30:00

BRANCH=47-rebuild-the-juglet-input-clouds-with-the-corpus-converter
CANON=/data/gpfs/projects/punim2657/sfs_preprocessing
RUNS=/data/gpfs/projects/punim2657/SfSpp/runs
PY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3
HERE=$(cd "$(dirname "$0")" && pwd)

[ -f "$HERE/submit47.sbatch.tmpl" ] || { echo "FATAL: submit47.sbatch.tmpl not beside me ($HERE)"; exit 1; }

echo "[submit47] fetch + resolve $BRANCH"
git -C "$CANON" fetch --no-tags origin "+refs/heads/*:refs/remotes/origin/*" > /dev/null
NEW=$(git -C "$CANON" rev-parse "origin/$BRANCH")
GIT7=$(git -C "$CANON" rev-parse --short=7 "$NEW")
echo "[submit47] commit $NEW ($GIT7)"

STAMP=$(date +%Y%m%d-%H%M)
RUNID=$STAMP'_'$GIT7'_t47-'$TAG
RUN=$RUNS/$RUNID
IXTAG=t47-$TAG
JOBNAME=t47-$TAG

echo "[submit47] run dir $RUN"
mkdir -p "$RUN/logs" "$RUN/out" "$RUN/instruments"
cp -f "$HERE"/gates47.py "$HERE"/figure47.py "$HERE"/submit47.sh \
      "$HERE"/submit47.sbatch.tmpl "$HERE"/COPIES.md "$RUN/instruments/"
if [ -f "$HERE/.gitattributes" ]; then cp -f "$HERE/.gitattributes" "$RUN/instruments/"; fi

echo "[submit47] render template"
TMPL=$RUN/instruments/submit47.sbatch.tmpl
OUTF=$RUN/submit.sbatch
"$PY" - "$TMPL" "$OUTF" "$JOBNAME" "$RUN" "$RUNID" "$NEW" "$IXTAG" "$WALL" <<'PYEOF'
import sys
tmpl, out = sys.argv[1], sys.argv[2]
vals = sys.argv[3:]
keys = ['__JOBNAME__', '__RUNDIR__', '__RUNID__', '__NEWCOMMIT__', '__IXTAG__', '__TIME__']
s = open(tmpl).read()
for k, v in zip(keys, vals):
    if k not in s:
        print('FATAL: placeholder ' + k + ' missing from template')
        sys.exit(3)
    s = s.replace(k, v)
open(out, 'w').write(s)
print('rendered ' + out + ' (' + str(len(s)) + ' bytes)')
PYEOF

echo "[submit47] gates on the rendered batch file"
CR=$(grep -c -F $(printf '\r') "$OUTF" || true)
[ "$CR" -eq 0 ] || { echo "FATAL: $CR CR bytes in rendered sbatch"; exit 4; }
LEFT=$(grep -o -E '__[A-Z][A-Z0-9_]*__' "$OUTF" | wc -l)
[ "$LEFT" -eq 0 ] || { echo "FATAL: $LEFT unrendered placeholders"; exit 5; }
bash -n "$OUTF" || { echo "FATAL: bash -n failed"; exit 6; }
EXP=$(grep -o -E '\$[A-Za-z_][A-Za-z0-9_]*' "$OUTF" | wc -l)
[ "$EXP" -ge 40 ] || { echo "FATAL: only $EXP expansions (expected >= 40: renderer mangled the script?)"; exit 7; }
"$PY" -m py_compile "$RUN/instruments/gates47.py" "$RUN/instruments/figure47.py"
echo "[submit47] gates ok (expansions=$EXP)"

echo "[submit47] sbatch"
JOBID=$(sbatch --parsable "$OUTF")
echo "[submit47] RUNID=$RUNID JOBID=$JOBID"

"$PY" - "$RUN/run.json" "$RUNID" "$JOBID" "$NEW" "$IXTAG" "$TAG" "$WALL" "$RUN" "$BRANCH" <<'PYEOF'
import json, sys, datetime
runid, jobid, commit, ixtag, tag, wall, run, branch = sys.argv[2:]
doc = {
    'runid': runid,
    'ticket': '47-rebuild-the-juglet-input-clouds-with-the-corpus-converter',
    'branch': branch,
    'commit': commit,
    'tag': tag,
    'index_tag': ixtag,
    'jobid': jobid,
    'walltime': wall,
    'run_dir': run,
    'submitted_at_utc': datetime.datetime.utcnow().replace(microsecond=0).isoformat() + 'Z',
    'submitter': 'stage47/instruments/submit47.sh (rendered submit.sbatch; job re-verifies vs commit)',
}
json.dump(doc, open(sys.argv[1], 'w'), indent=2, sort_keys=True)
print('wrote ' + sys.argv[1])
PYEOF

squeue -j "$JOBID" -o "%i %P %j %u %T %M %D %R"
echo "[submit47] submitted. poll with: bash /c/PR/scripts/slurm_poll.sh $JOBID"
