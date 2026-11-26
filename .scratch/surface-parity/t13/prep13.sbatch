#!/bin/bash
#SBATCH --job-name=t13-prep
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=32G
#SBATCH --time=02:00:00
#SBATCH --output=logs/slurm-prep-%j.out
#SBATCH --error=logs/slurm-prep-%j.err
#
# Ticket 13 prep: pin the shared executable, run the Part B surface-factor study (j01_factors13.py),
# stage one 12-file axis pack per Part A arm, write the array map, then submit the 22-cell array
# plus a dependent REPORT job.  Nothing here rebuilds the binary: it is hardlinked from the pinned
# t13-recip build and verified against WANT_SHA inside the container by cell13.sbatch.
set -uo pipefail

RUN=$SLURM_SUBMIT_DIR
WORK=$RUN/work/t13
PANEL=$RUN/panel
SRC_EXE=/data/gpfs/projects/punim2657/SfSpp/runs/20261122-1612_651fee0_t13-j01-recip/work/build/Hierarchy-T13
WANT_SHA=de44ffc23c8db5208bd5f6f9c9f57d819bed7805f0330526bcb2750487bfd727
PY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3
CORP=/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp
TREE=/data/gpfs/projects/punim2657/SfSpp/runs/20261125-1451_a50f8cc_t09-potJ/trees/J_K3R1/J/MM
T08_AX=/data/gpfs/projects/punim2657/SfSpp/runs/20261125-1218_fc5d0ac_t08-ship/out/axes08_own_dedup
T09_AX=/data/gpfs/projects/punim2657/SfSpp/runs/20261125-1340_a50f8cc_t09-own-surfaces/out/axes09_own_regen
SHIP=/data/gpfs/projects/punim2657/SfSpp/runs/20261121-1319_2e951d9_t03-ship
SHIP_TRI=$SHIP/out/axes03_tri
mkdir -p "$RUN/logs" "$RUN/evidence" "$RUN/axes" "$RUN/out" "$RUN/score" "$RUN/mount"
print_status() { echo "$@" | tee -a "$RUN/logs/run_status.txt"; }
fail() { local rc=$1; shift; print_status "RUN-FAIL $rc :: $*"; exit "$rc"; }

print_status "prep-start $(date -u +%FT%TZ) job=$SLURM_JOB_ID"
date -u +%FT%TZ > "$RUN/logs/submit_time.txt"

# ---- 1. the shared executable: hardlink (or copy) + the in-container checksum list -----------
mkdir -p "$PANEL/build" "$PANEL/logs"
[ -x "$SRC_EXE" ] || fail 11 "pinned executable missing: $SRC_EXE"
if [ ! -f "$PANEL/build/Hierarchy-T13" ]; then
  ln "$SRC_EXE" "$PANEL/build/Hierarchy-T13" 2>/dev/null || cp "$SRC_EXE" "$PANEL/build/Hierarchy-T13"
fi
GOT=$(sha256sum "$PANEL/build/Hierarchy-T13" | cut -d' ' -f1)
printf '%s  /panel/build/Hierarchy-T13\n' "$WANT_SHA" > "$PANEL/logs/executable.sha256"
[ "$GOT" = "$WANT_SHA" ] || fail 13 "panel executable sha mismatch got=$GOT want=$WANT_SHA"
print_status "[PANEL] exe_sha=$GOT (WANT_SHA match)"

# ---- 2. corpus fingerprint BEFORE anything reads or writes it --------------------------------
"$PY" "$SHIP/work/corpus_md5_t03.py" --out "$RUN/logs/corpus_md5_before.txt" > "$RUN/logs/corpus_before.log" 2>&1
MD5_RC=$?
print_status "[CORPUS] before rc=$MD5_RC lines=$(wc -l < "$RUN/logs/corpus_md5_before.txt" 2>/dev/null)"

# ---- 3. Part B: the nine surface-factor arms through the frozen SHIP selector ---------------
"$PY" "$WORK/j01_factors13.py" --run "$RUN" > "$RUN/logs/j01_stdout.log" 2>&1
J01_RC=$?
print_status "[J01] rc=$J01_RC"
# ---- 4. one 12-file axis pack per Part A arm ------------------------------------------------
NAMES=$(cd "$TREE/Axes" && ls *_Axis.xyz | sort)
CNT=$(printf '%s\n' "$NAMES" | wc -l)
[ "$CNT" -eq 12 ] || fail 14 "expected 12 Pot J axis files in $TREE/Axes, found $CNT"
print_status "[AXES] source names=$CNT"

stage_all() {
  local arm=$1 src=$2 n
  rm -rf "$RUN/axes/$arm"
  mkdir -p "$RUN/axes/$arm"
  for n in $NAMES; do
    [ -f "$src/$n" ] || fail 14 "axis source missing: $src/$n"
    cp "$src/$n" "$RUN/axes/$arm/$n" || fail 14 "copy failed: $src/$n"
  done
}
stage_one() {
  local arm=$1 name=$2 src=$3
  [ -f "$src/$name" ] || fail 14 "swap source missing: $src/$name"
  cp "$src/$name" "$RUN/axes/$arm/$name" || fail 14 "swap copy failed: $src/$name"
}
changed_count() {
  local arm=$1 n c=0
  for n in $NAMES; do
    cmp -s "$T09_AX/$n" "$RUN/axes/$arm/$n" || c=$((c + 1))
  done
  echo "$c"
}

stage_all MOR_CTL "$CORP/Axes"
stage_all T08_ALL "$T08_AX"
stage_all T09_ALL "$T09_AX"
stage_all T09_WITH_AUTHOR_J01 "$T09_AX"
stage_one T09_WITH_AUTHOR_J01 Pot_J_Piece_01_Axis.xyz "$SHIP_TRI"
for k in 01 02 05 06 11; do
  stage_all SWAP_J$k "$T09_AX"
  stage_one SWAP_J$k "Pot_J_Piece_"$k"_Axis.xyz" "$T08_AX"
done

: > "$RUN/logs/axis_diff.tsv"
for arm in MOR_CTL T08_ALL T09_ALL T09_WITH_AUTHOR_J01 SWAP_J01 SWAP_J02 SWAP_J05 SWAP_J06 SWAP_J11; do
  C=$(changed_count "$arm")
  printf '%s\t%s\n' "$arm" "$C" >> "$RUN/logs/axis_diff.tsv"
done
cat "$RUN/logs/axis_diff.tsv" | tee -a "$RUN/logs/run_status.txt"

# ---- 5. the array map: 22 Part A cells -------------------------------------------------------
IDX=0
emit() {
  printf '%s\t%s\t%s\t%s\t%s\n' "$IDX" "partA" "$1" "$2" "$RUN/axes/$1" >> "$RUN/logs/array_map.tsv"
  IDX=$((IDX + 1))
}
: > "$RUN/logs/array_map.tsv"
emit MOR_CTL 1;  emit MOR_CTL 2
emit T08_ALL 1;  emit T08_ALL 2;  emit T08_ALL 3;  emit T08_ALL 4
emit T09_ALL 1;  emit T09_ALL 2;  emit T09_ALL 3;  emit T09_ALL 4
emit T09_WITH_AUTHOR_J01 1; emit T09_WITH_AUTHOR_J01 2
emit SWAP_J01 1; emit SWAP_J01 2
emit SWAP_J02 1; emit SWAP_J02 2
emit SWAP_J05 1; emit SWAP_J05 2
emit SWAP_J06 1; emit SWAP_J06 2
emit SWAP_J11 1; emit SWAP_J11 2
[ "$IDX" -eq 22 ] || fail 15 "array map has $IDX rows, expected 22"

# ---- 6. submit the array and a dependent report job -----------------------------------------
cd "$RUN" || fail 16 "cannot cd $RUN"
SB=$(sbatch --parsable --array=0-21%4 "$WORK/cell13.sbatch" | tail -1)
[ -n "$SB" ] || fail 17 "array submission failed"
RB=$(sbatch --parsable --dependency=afterany:"$SB" "$WORK/cell13.sbatch" REPORT report | tail -1)
echo "$SB" > "$RUN/logs/array_job.txt"
echo "$RB" > "$RUN/logs/report_job.txt"
printf 'submit\t%s\t-\t-\nreport\t%s\t-\t-\n' "$SB" "$RB" > "$RUN/logs/parent_jobs.tsv"
print_status "[SUBMIT] array=$SB report=$RB"

printf '{\n  "prep_job": "%s",\n  "array_job": "%s",\n  "report_job": "%s",\n  "exe_sha": "%s",\n  "exe_sha_ok": %s,\n  "corpus_md5_rc": %s,\n  "j01_rc": %s,\n  "axis_names": %s,\n  "array_cells": %s,\n  "submitted_utc": "%s"\n}\n' \
  "$SLURM_JOB_ID" "$SB" "$RB" "$GOT" "$([ "$GOT" = "$WANT_SHA" ] && echo 1 || echo 0)" "$MD5_RC" "$J01_RC" "$CNT" "$IDX" "$(cat "$RUN/logs/submit_time.txt")" \
  > "$RUN/logs/prep_status.json"
print_status "prep-done $(date -u +%FT%TZ)"
exit 0
