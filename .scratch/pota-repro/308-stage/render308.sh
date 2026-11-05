#!/bin/bash
# render308.sh -- submit the Stage D render job for the pots that finished.
#   render308.sh [POT ...]     (default: the pots in /tmp/t308b_jobs.txt)
set -uo pipefail
SSH=/c/Windows/System32/OpenSSH/ssh.exe
SCP=/c/Windows/System32/OpenSSH/scp.exe
HOST=spartan
RUNS=/data/gpfs/projects/punim2657/SfSpp/runs
STAGE=/tmp/s308r
LOC=$(cd "$(dirname "$0")" && pwd)
rssh() { local i; for i in $(seq 1 12); do $SSH $HOST "$1" && return 0; sleep 10; done; return 1; }
rscp() { local i; for i in $(seq 1 12); do "$SCP" -q -o ConnectTimeout=25 "$1" "$HOST:$2" && return 0; echo "   (scp retry $i)" >&2; sleep 10; done; return 1; }

POTS=("$@")
if [ ${#POTS[@]} -eq 0 ]; then mapfile -t POTS < <(cut -d: -f1 /tmp/t308b_jobs.txt 2>/dev/null); fi
[ ${#POTS[@]} -gt 0 ] || { echo "no pots"; exit 2; }

RUN=$RUNS/$(date +%Y%m%d-%H%M)_d330469_t308d-render
echo "RUN=$RUN"
rssh "mkdir -p $RUN/logs $RUN/out $STAGE" || exit 1

# work files, CR-stripped (a CRLF helper dies inside the SIF -- ticket 308's first
# Stage B submission failed exactly that way)
rm -rf /tmp/s308r_local && mkdir -p /tmp/s308r_local
for f in render305.py specgen308.py; do
  cp "$LOC/../305-stage/$f" /tmp/s308r_local/$f 2>/dev/null || cp "$LOC/$f" /tmp/s308r_local/$f
done
cp "$LOC/render308.sbatch" /tmp/s308r_local/render308.sbatch
for f in /tmp/s308r_local/*; do sed -i 's/\r$//' "$f"; done
rssh "rm -rf $STAGE && mkdir -p $STAGE" || exit 1
for f in /tmp/s308r_local/*; do rscp "$f" "$STAGE/$(basename $f)" || exit 1; done
rscp /tmp/s308r_local/render308.sbatch "$RUN/submit.sbatch" || exit 1
rssh "mkdir -p $RUN/work" || exit 1
for f in /tmp/s308r_local/*.py; do rscp "$f" "$RUN/work/$(basename $f)" || exit 1; done

# spec.tsv: pots + the Juglet pair.  The run dirs live on Spartan, so the lookup and the
# spec build both happen there -- a local ls here silently found nothing once.
DIRS=$(rssh "for P in ${POTS[*]}; do ls -d $RUNS/*t308b-\$P 2>/dev/null | tail -1; done" | tr "\n" " " | sed "s/ *$//")
echo "--- run dirs"; echo "$DIRS"
[ -n "$DIRS" ] || { echo "ABORT: no pot run dirs found"; exit 1; }
rssh "python3 $STAGE/specgen308.py $DIRS > $RUN/spec.tsv" || exit 1
JUG=$(rssh "ls -d $RUNS/*t308c-jug 2>/dev/null | tail -1")
if [ -n "$JUG" ]; then
  rssh "printf 'JUG\\tJuglet 9 pieces, floor 20, our axes (N) vs authors axes (O), NP 9\\tN20=%s/out/F20N_r1 O20=%s/out/F20O_r1\\n' $JUG $JUG >> $RUN/spec.tsv"
fi
echo "--- spec.tsv"; rssh "cat $RUN/spec.tsv"
cat > /tmp/run308d.json <<EOF
{"ticket":"308","stage":"D-render","commit":"d330469","created":"$(date -u +%FT%TZ)",
 "what":"one figure per pot: best repeat of OO/MM/MMp, top and side in one shared view box",
 "note":"a data plot of placed pieces and their edgelines, not a photograph"}
EOF
rscp /tmp/run308d.json "$RUN/run.json" || exit 1

JOB=$(rssh "cd $RUN && if [ -s sbatch.id ]; then cat sbatch.id; else sbatch --parsable submit.sbatch > sbatch.id 2> sbatch.err; cat sbatch.id; fi" | tail -1 | tr -d ' \r')
echo "JOB=$JOB"
[ -n "$JOB" ] || { echo "ABORT: no job id"; cat /tmp/s308r_local/../sbatch.err 2>/dev/null; exit 1; }
echo "$JOB" > /tmp/t308d_job.txt
rssh "printf '%s\\t%s\\t%s\\t%s\\t\\t\\n' '$(basename $RUN)' '$JOB' 'd330469' 't308d-render' >> $RUNS/index.tsv"
echo "submitted; poll with scripts/slurm_poll.sh $JOB"