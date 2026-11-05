#!/bin/bash
# Ticket 310 stage C launcher: seating with the basin rule's axes (and the authors' axes
# as the same-job control).  One Slurm job per pot, so MO and MM run on the same binary,
# the same include and the same session; the axes-only substitution is proved by diff -rq
# in the job itself (logs/substitution.tsv).
#
#   POTS="A"        ARMSPEC="MM:10"        -> C1: ten repeats of our breaklines + rule axes
#   POTS="A B ..."  ARMSPEC="MO:2 MM:2"    -> C2: our axes against the authors' axes
#
# Re-running is safe: pots already in /tmp/t310e_jobs.txt are skipped, and sbatch is
# guarded by the run dir's sbatch.id so a dropped ssh connection cannot submit twice.
set -euo pipefail
export MSYS_NO_PATHCONV=1 MSYS2_ARG_CONV_EXCL='*'
SSH="/c/Windows/System32/OpenSSH/ssh.exe"
SCP="/c/Windows/System32/OpenSSH/scp.exe"
rssh() { local i; for i in $(seq 1 12); do "$SSH" -o ConnectTimeout=25 -o ServerAliveInterval=10 spartan "$1" && return 0; echo "   (ssh retry $i)" >&2; sleep 10; done; return 1; }
rscp() { local i; for i in $(seq 1 12); do "$SCP" -o ConnectTimeout=25 "$@" && return 0; echo "   (scp retry $i)" >&2; sleep 10; done; return 1; }

WT=C:/PR/worktrees/sfs/310
STAGE=$WT/.scratch/pota-repro/310-stage
S305=$WT/.scratch/pota-repro/305-stage
S306=$WT/.scratch/pota-repro/306-stage
S308=$WT/.scratch/pota-repro/308-stage
RUNS=/data/gpfs/projects/punim2657/SfSpp/runs
CORP=/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp
LT="$(cygpath -w /tmp)"

POTS="${POTS:-A}"
# One record file per campaign: C1 (pot A, ten repeats) and C2 (pots A-J, arms) are
# different runs of the same pot and must not skip each other.
JF="${JF:-/tmp/t310e_jobs.txt}"
ARMSPEC="${ARMSPEC:-MO:2 MM:2}"
TAG="${TAG:-t310c-seat}"
# The B3 corpus run (tagged -timing because it began as the 3-piece runtime probe and
# was submitted without ONLY, so it processed all 163 pieces).
AXP="${AXP:-$RUNS/20261105-1215_1a6f16e_t310b3-timing/out/axes310}"
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
# An axis file must exist for every piece of every pot this job will seat.  The corpus
# run (B3) finishes pieces in completion order, so a pot is ready before the whole 163
# are; requiring 163 would hold C1 behind Pot J for no reason.
n=$(rssh "ls $AXP/*.xyz 2>/dev/null | wc -l")
echo "   AXP=$AXP: $n files"
for p in $POTS; do
  need=$(rssh "ls $CORP/Surfaces/Pot_${p}_Piece_*_Surface_0.xyz 2>/dev/null | wc -l")
  have=$(rssh "ls $AXP/Pot_${p}_Piece_*_Axis.xyz 2>/dev/null | wc -l")
  echo "   pot $p axes $have / $need"
  [ "$have" -ge "$need" ] && [ "$need" -gt 0 ] || { echo "ABORT: pot $p axes not ready in AXP"; exit 1; }
done
for p in $POTS; do
  case $p in A) L=$LANES_A;; B) L=$LANES_B;; C) L=$LANES_C;; D) L=$LANES_D;;
    E) L=$LANES_E;; F) L=$LANES_F;; G) L=$LANES_G;; I) L=$LANES_I;; J) L=$LANES_J;;
    *) echo "ABORT: unknown pot $p"; exit 1;; esac
  c=$(rssh "ls $L/*.Bl0 2>/dev/null | wc -l"); echo "   pot $p lanes $c"
  [ "$c" -ge 4 ] || { echo "ABORT: lanes for $p"; exit 1; }
done

cd "$WT"
rm -rf sfs_axes/__pycache__
rm -rf /tmp/s310ework && mkdir -p /tmp/s310ework
cp "$S305/arm67.sh" "$S305/patch_guard67.py" "$S305/mk_inc.py" "$S305/stage305.py" \
   "$S305/acc305.py" "$S305/score305.py" "$S306/idx_append.py" /tmp/s310ework/
sed -i 's/\r$//' /tmp/s310ework/*
if grep -l "$(printf '\r')" /tmp/s310ework/* >/dev/null 2>&1; then echo "ABORT: CR survived"; exit 1; fi
echo -n "$COMMIT" > /tmp/code_commit.txt

submit_pot() {  # $1=pot $2=named $3=np $4=lanes
  local POT=$1 NAMED=$2 NP=$3 LANES=$4
  local TS RUNID RUN JOB
  if awk '{print $1}' "$JF" 2>/dev/null | grep -qx "$POT"; then
    echo "-- pot $POT already submitted, skip"; return 0; fi
  TS=$(rssh 'date -u +%Y%m%d-%H%M') || { echo "ABORT: no ssh"; exit 1; }
  RUNID="${TS}_${COMMIT}_${TAG}-$POT"
  RUN="$RUNS/$RUNID"
  echo "-- pot $POT named=$NAMED np=$NP -> $RUNID"
  rssh "mkdir -p $RUN/logs $RUN/work $RUN/out $RUN/score" || { echo "ABORT: mkdir"; exit 1; }

  cat > /tmp/run310e_$POT.json <<EOF
{
  "runid": "$RUNID",
  "ticket": "310",
  "stage": "C: pot $POT seating, arms '$ARMSPEC' in one allocation",
  "template": "308-stage/e2e308.sbatch (unchanged; the ticket-308 harness)",
  "commit": "$COMMIT",
  "pot": "$POT", "named": $NAMED, "np": $NP, "floor": $FLOOR,
  "armspec": "$ARMSPEC",
  "lanes": "$LANES",
  "axes": { "MO": "$CORP/Axes (authors, read-only)", "MM": "$AXP", "MMp": "$AXP" },
  "corpus": "$CORP (read-only; md5 of every input this pot reads, before and after)",
  "note": "MM = our rule axes; MO = the authors' axes on the same staged breaklines; diff -rq in-job proves the substitution is axes-only"
}
EOF

  sed 's/\r$//' "$S308/e2e308.sbatch" \
    | sed -e "s|__POT__|$POT|g" -e "s|__NAMED__|$NAMED|g" -e "s|__NP__|$NP|g" \
          -e "s|__FLOOR__|$FLOOR|g" -e "s|__ARMSPEC__|$ARMSPEC|g" \
          -e "s|__LANES__|$LANES|g" -e "s|__AXC__|$CORP/Axes|g" \
          -e "s|__AXP__|$AXP|g" -e "s|__AXQ__|$AXP|g" \
          -e "s|__SEEDS__|NONE|g" -e "s|__SEEDDIR__|NONE|g" \
    > /tmp/e2e310e_$POT.sbatch
  { grep -c "__" /tmp/e2e310e_$POT.sbatch || true; } | sed 's/^/   leftover placeholders: /'

  rscp "$LT\\run310e_$POT.json" "spartan:$RUN/run.json" || { echo "ABORT: run.json"; exit 1; }
  rscp "$LT\\e2e310e_$POT.sbatch" "spartan:$RUN/submit.sbatch" || { echo "ABORT: submit"; exit 1; }
  # scp.exe with MSYS_NO_PATHCONV=1 needs WINDOWS-form local paths; /tmp/s310ework/...
  # is an MSYS path it cannot open (ticket 310, C1 first attempt aborted here).
  for f in arm67.sh patch_guard67.py mk_inc.py stage305.py acc305.py score305.py \
           idx_append.py; do
    rscp "$LT\\s310ework\\$f" "spartan:$RUN/work/$f" || { echo "ABORT: work/$f"; exit 1; }
  done
  rscp "$LT\\code_commit.txt" "spartan:$RUN/work/code_commit.txt" || { echo "ABORT: commit"; exit 1; }

  rssh "cd $RUN && md5sum submit.sbatch work/arm67.sh work/stage305.py" || { echo "ABORT: md5"; exit 1; }
  JOB=$(rssh "cd $RUN && if [ -s sbatch.id ]; then cat sbatch.id; else sbatch --parsable submit.sbatch > sbatch.id 2> sbatch.err; cat sbatch.id; fi" | tail -1 | tr -d ' \r')
  echo "   JOB=$JOB"
  [ -n "$JOB" ] || { echo "ABORT: sbatch gave no job id; see $RUN/sbatch.err"; exit 1; }
  rssh "python3 $RUN/work/idx_append.py $RUNID $JOB $COMMIT $TAG-$POT" | tail -1
  echo "   $POT $JOB $RUNID" >> "$JF"
}

touch "$JF"
for p in $POTS; do
  case $p in
    A) submit_pot A 8  8  "$LANES_A";;
    B) submit_pot B 9  9  "$LANES_B";;
    C) submit_pot C 4  4  "$LANES_C";;
    D) submit_pot D 29 29 "$LANES_D";;
    E) submit_pot E 31 31 "$LANES_E";;
    F) submit_pot F 7  7  "$LANES_F";;
    G) submit_pot G 7  7  "$LANES_G";;
    I) submit_pot I 30 30 "$LANES_I";;
    J) submit_pot J 12 19 "$LANES_J";;
  esac
done
echo "== submitted"
cat "$JF"
