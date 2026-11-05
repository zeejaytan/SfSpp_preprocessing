#!/bin/bash
# Ticket 308 Stage C launcher: the Juglet floor sweep, one job.
# Floors 5/10/15/20/30 x {authors' Dataset axes, our paper axes} x 2 repeats, NP 9.
# The axis files are the ONLY difference between the O and N tree (proved by diff -rq).
set -euo pipefail
SSH="/c/Windows/System32/OpenSSH/ssh.exe"
SCP="/c/Windows/System32/OpenSSH/scp.exe"
rssh() { local i; for i in $(seq 1 12); do "$SSH" -o ConnectTimeout=25 spartan "$1" && return 0; echo "   (ssh retry $i)" >&2; sleep 10; done; return 1; }
rscp() { local i; for i in $(seq 1 12); do "$SCP" -o ConnectTimeout=25 "$@" && return 0; echo "   (scp retry $i)" >&2; sleep 10; done; return 1; }
WT=C:/PR/worktrees/sfs/308
STAGE=$WT/.scratch/pota-repro/308-stage
S305=$WT/.scratch/pota-repro/305-stage
S306=$WT/.scratch/pota-repro/306-stage
S307H=$WT/.scratch/pota-repro/307-stage/helpers
RUNS=/data/gpfs/projects/punim2657/SfSpp/runs
SA="${SA:-$RUNS/20261105-0532_d330469_t308a-axes}"
JAXO=/data/gpfs/projects/punim2657/sfs_preprocessing/Dataset/Axes/Juglet
JAXN="$SA/out/jug/axes_paper"
FLOORS="${FLOORS:-5 10 15 20 30}"
REPS="${REPS:-2}"
COMMIT=$(git -C "$WT" rev-parse --short=7 HEAD)

echo "== pre-flight"
n=$(rssh "ls $JAXO/*.xyz 2>/dev/null | wc -l"); echo "   authors axes: $n"; [ "$n" -eq 9 ] || { echo ABORT; exit 1; }
n=$(rssh "ls $JAXN/*.xyz 2>/dev/null | wc -l"); echo "   our axes: $n"; [ "$n" -eq 9 ] || { echo ABORT; exit 1; }
n=$(rssh "ls /data/gpfs/projects/punim2657/SfSpp/runs/20261103-1332_fab76f5_t66-admitsign-default/outU_jug/geom/*.Bl0 2>/dev/null | wc -l"); echo "   jug lanes: $n"; [ "$n" -eq 9 ] || { echo ABORT; exit 1; }

rm -rf /tmp/s308c && mkdir -p /tmp/s308c
cp "$S305/arm67.sh" "$S305/patch_guard67.py" "$S305/mk_inc.py" "$S305/stage67_inputs.py" \
   "$S305/acc305.py" "$S307H/score58.py" "$S306/idx_append.py" "$STAGE/jug308_c2.py" /tmp/s308c/
sed -i 's/\r$//' /tmp/s308c/*
echo -n "$COMMIT" > /tmp/code_commit.txt

TS=$(rssh 'date -u +%Y%m%d-%H%M')
RUNID="${TS}_${COMMIT}_t308c-jug"
RUN="$RUNS/$RUNID"
echo "-- juglet floor sweep -> $RUNID (floors: $FLOORS, reps $REPS)"
rssh "mkdir -p $RUN/logs $RUN/work $RUN/out $RUN/score" || exit 1

cat > /tmp/run.json.t308c <<EOF
{
  "runid": "$RUNID",
  "ticket": "308",
  "stage": "C: Juglet floor sweep",
  "template": "308-stage/jug308.sbatch",
  "commit": "$COMMIT",
  "floors": "$FLOORS",
  "reps": $REPS,
  "np": 9,
  "lanes": "/data/gpfs/projects/punim2657/SfSpp/runs/20261103-1332_fab76f5_t66-admitsign-default/outU_jug/geom",
  "axes": {"authors": "$JAXO", "ours": "$JAXN"},
  "block": "/data/gpfs/projects/punim2657/SfSpp/runs/20261101-1913_d8f716f_t58-floor-density-panel/work/juglet_orig_block.inc",
  "note": "floor changes only the admission gate; the two trees differ only in Axes/ (diff -rq proof in logs/diff_O_vs_N.txt)"
}
EOF

sed 's/\r$//' "$STAGE/jug308.sbatch" \
  | sed -e "s|__JAXO__|$JAXO|g" -e "s|__JAXN__|$JAXN|g" \
        -e "s|__FLOORS__|$FLOORS|g" -e "s|__REPS__|$REPS|g" > /tmp/jug308.sbatch
{ grep -c "__" /tmp/jug308.sbatch || true; } | sed 's/^/   leftover placeholders: /'

rscp /tmp/run.json.t308c "spartan:$RUN/run.json" || exit 1
rscp /tmp/jug308.sbatch "spartan:$RUN/submit.sbatch" || exit 1
rscp /tmp/s308c/arm67.sh /tmp/s308c/patch_guard67.py /tmp/s308c/mk_inc.py \
     /tmp/s308c/stage67_inputs.py /tmp/s308c/acc305.py /tmp/s308c/score58.py \
     /tmp/s308c/idx_append.py /tmp/s308c/jug308_c2.py "spartan:$RUN/work/" || exit 1
rscp /tmp/code_commit.txt "spartan:$RUN/work/code_commit.txt" || exit 1
rm -f /tmp/run.json.t308c

rssh "cd $RUN && md5sum submit.sbatch work/*.py work/arm67.sh" || exit 1
JOB=$(rssh "cd $RUN && if [ -s sbatch.id ]; then cat sbatch.id; else sbatch --parsable submit.sbatch > sbatch.id 2> sbatch.err; cat sbatch.id; fi" | tail -1 | tr -d ' \r')
echo "   JOB=$JOB"
[ -n "$JOB" ] || { echo "ABORT: no job id"; exit 1; }
rssh "python3 $RUN/work/idx_append.py $RUNID $JOB $COMMIT t308c-jug" | tail -1
echo "   jug $JOB $RUNID" >> /tmp/t308c_jobs.txt
cat /tmp/t308c_jobs.txt
