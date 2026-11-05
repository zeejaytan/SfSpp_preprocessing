#!/bin/bash
# Ticket 308 Stage B launcher: one job per pot, three arms in one allocation.
# Creates each run dir, bakes the per-pot template, copies the instruments, submits,
# records the index row.  Nothing is committed by this script.
#
# Re-running is safe: pots already in /tmp/t308b_jobs.txt are skipped, and sbatch is
# guarded by the run dir's sbatch.id so a dropped ssh connection cannot submit twice.
set -euo pipefail
SSH="/c/Windows/System32/OpenSSH/ssh.exe"
SCP="/c/Windows/System32/OpenSSH/scp.exe"
rssh() { local i; for i in $(seq 1 12); do "$SSH" -o ConnectTimeout=25 -o ServerAliveInterval=10 spartan "$1" && return 0; echo "   (ssh retry $i)" >&2; sleep 10; done; return 1; }
rscp() { local i; for i in $(seq 1 12); do "$SCP" -o ConnectTimeout=25 "$@" && return 0; echo "   (scp retry $i)" >&2; sleep 10; done; return 1; }
WT=C:/PR/worktrees/sfs/308
STAGE=$WT/.scratch/pota-repro/308-stage
S305=$WT/.scratch/pota-repro/305-stage
S306=$WT/.scratch/pota-repro/306-stage
RUNS=/data/gpfs/projects/punim2657/SfSpp/runs
CORP=/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp
SA="${SA:-$RUNS/20261105-0532_d330469_t308a-axes}"
AXP="$SA/out/axes_paper"
AXQ="$SA/out/axes_prune"
SEEDDIR="$SA/out/pota"
ARMSPEC="${ARMSPEC:-MO:2 MM:2 MMp:2}"
FLOOR=50
COMMIT=$(git -C "$WT" rev-parse --short=7 HEAD)

LANES_A=$RUNS/20261103-1332_fab76f5_t66-admitsign-default/outU_pota/geom
LANES_B=$RUNS/20261105-0445_9c5eec2_t305-lane-b2/out/geom
LANES_C=$RUNS/20261105-0445_9c5eec2_t305-lane-c2/out/geom
LANES_D=$RUNS/20261105-0445_9c5eec2_t305-lane-d2/out/geom
LANES_E=$RUNS/20261105-0445_9c5eec2_t305-lane-e2/out/geom
LANES_F=$RUNS/20261105-0520_9c5eec2_t305-lane-f3/out/geom
LANES_G=$RUNS/20261105-0445_9c5eec2_t305-lane-g2/out/geom
LANES_I=$RUNS/20261105-0520_9c5eec2_t305-lane-i3/out/geom
LANES_J=$RUNS/20261105-0520_9c5eec2_t305-lane-j3/out/geom

echo "== pre-flight"
for f in "$AXP" "$AXQ"; do
  n=$(rssh "ls $f/*.xyz 2>/dev/null | wc -l")
  echo "   $f: $n files"
  [ "$n" -eq 163 ] || { echo "ABORT: expected 163 axis files"; exit 1; }
done
[ "$(rssh "ls $SEEDDIR/paper_s*/Pot_A_Piece_*_Axis.xyz 2>/dev/null | wc -l")" -eq 64 ] \
  || { echo "ABORT: expected 64 Pot A seed axis files"; exit 1; }

cd "$WT"
rm -rf sfs_axes/__pycache__
# The laptop checkout is CRLF; a bash helper copied as-is dies inside the SIF with
# "syntax error near unexpected token" and the arm exits 2 in zero seconds.  Ship
# clean copies.
rm -rf /tmp/s308work && mkdir -p /tmp/s308work
cp "$S305/arm67.sh" "$S305/patch_guard67.py" "$S305/mk_inc.py" "$S305/stage305.py" \
   "$S305/acc305.py" "$S305/score305.py" "$S306/idx_append.py" /tmp/s308work/
sed -i 's/\r$//' /tmp/s308work/*
if grep -l "$(printf '\r')" /tmp/s308work/* >/dev/null 2>&1; then echo "ABORT: CR survived"; exit 1; fi
echo -n "$COMMIT" > /tmp/code_commit.txt

submit_pot() {  # $1=pot $2=named $3=np $4=lanes $5=seeds $6=seeddir
  local POT=$1 NAMED=$2 NP=$3 LANES=$4 SEEDS=$5 SEEDDIRV=$6
  local TS RUNID RUN JOB
  if awk '{print $1}' /tmp/t308b_jobs.txt 2>/dev/null | grep -qx "$POT"; then
    echo "-- pot $POT already submitted, skip"; return 0; fi
  TS=$(rssh 'date -u +%Y%m%d-%H%M') || { echo "ABORT: no ssh"; exit 1; }
  RUNID="${TS}_${COMMIT}_t308b-${POT}"
  RUN="$RUNS/$RUNID"
  echo "-- pot $POT named=$NAMED np=$NP -> $RUNID"
  rssh "mkdir -p $RUN/logs $RUN/work $RUN/out $RUN/score" || { echo "ABORT: mkdir $RUN"; exit 1; }

  cat > "$STAGE/run.json.t308b" <<EOF
{
  "runid": "$RUNID",
  "ticket": "308",
  "stage": "B: pot $POT, three arms in one allocation",
  "template": "308-stage/e2e308.sbatch",
  "commit": "$COMMIT",
  "pot": "$POT",
  "named": $NAMED,
  "np": $NP,
  "floor": $FLOOR,
  "armspec": "$ARMSPEC",
  "seeds": "$SEEDS",
  "lanes": "$LANES",
  "axes": {
    "control_MO": "$CORP/Axes",
    "paper_MM": "$AXP",
    "prune_MMp": "$AXQ",
    "seed_dir": "$SEEDDIRV"
  },
  "mapping": {
    "ticket OO": "arm MO (our breaklines + the authors' axes)",
    "ticket MM": "arm MM (our breaklines + our axes, shipped default)",
    "ticket MMp": "arm MMp (the same axes with SFS_AXES_COST_PRUNE=1)"
  },
  "corpus": "$CORP (read-only; md5 of every input this pot reads, before and after)",
  "note": "one stage305.py call per arm so the substitution is axes-only and provable with diff -rq"
}
EOF

  sed 's/\r$//' "$STAGE/e2e308.sbatch" \
    | sed -e "s|__POT__|$POT|g" -e "s|__NAMED__|$NAMED|g" -e "s|__NP__|$NP|g" \
          -e "s|__FLOOR__|$FLOOR|g" -e "s|__ARMSPEC__|$ARMSPEC|g" \
          -e "s|__LANES__|$LANES|g" -e "s|__AXC__|$CORP/Axes|g" \
          -e "s|__AXP__|$AXP|g" -e "s|__AXQ__|$AXQ|g" \
          -e "s|__SEEDS__|$SEEDS|g" -e "s|__SEEDDIR__|$SEEDDIRV|g" \
    > /tmp/e2e308_$POT.sbatch
  { grep -c "__" /tmp/e2e308_$POT.sbatch || true; } | sed 's/^/   leftover placeholders: /'

  rscp "$STAGE/run.json.t308b" "spartan:$RUN/run.json" || { echo "ABORT: scp run.json"; exit 1; }
  rscp /tmp/e2e308_$POT.sbatch "spartan:$RUN/submit.sbatch" || { echo "ABORT: scp submit"; exit 1; }
  rscp /tmp/s308work/arm67.sh /tmp/s308work/patch_guard67.py /tmp/s308work/mk_inc.py \
         /tmp/s308work/stage305.py /tmp/s308work/acc305.py /tmp/s308work/score305.py \
         /tmp/s308work/idx_append.py "spartan:$RUN/work/" || { echo "ABORT: scp work"; exit 1; }
  rscp /tmp/code_commit.txt "spartan:$RUN/work/code_commit.txt" || { echo "ABORT: scp commit"; exit 1; }
  rm -f "$STAGE/run.json.t308b"

  rssh "cd $RUN && md5sum submit.sbatch work/arm67.sh work/stage305.py" || { echo "ABORT: md5"; exit 1; }
  JOB=$(rssh "cd $RUN && if [ -s sbatch.id ]; then cat sbatch.id; else sbatch --parsable submit.sbatch > sbatch.id 2> sbatch.err; cat sbatch.id; fi" | tail -1 | tr -d ' \r')
  echo "   JOB=$JOB"
  [ -n "$JOB" ] || { echo "ABORT: sbatch gave no job id; see $RUN/sbatch.err"; exit 1; }
  rssh "python3 $RUN/work/idx_append.py $RUNID $JOB $COMMIT t308b-$POT" | tail -1
  echo "   $POT $JOB $RUNID" >> /tmp/t308b_jobs.txt
}

touch /tmp/t308b_jobs.txt
submit_pot A 8  8  "$LANES_A" "0,1,2,3,4,5,6,7" "$SEEDDIR"
submit_pot B 9  9  "$LANES_B" NONE NONE
submit_pot C 4  4  "$LANES_C" NONE NONE
submit_pot D 29 29 "$LANES_D" NONE NONE
submit_pot E 31 31 "$LANES_E" NONE NONE
submit_pot F 7  7  "$LANES_F" NONE NONE
submit_pot G 7  7  "$LANES_G" NONE NONE
submit_pot I 30 30 "$LANES_I" NONE NONE
submit_pot J 12 19 "$LANES_J" NONE NONE

echo "== submitted"
cat /tmp/t308b_jobs.txt