#!/bin/bash
#SBATCH --job-name=t16-prep
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
# Ticket 16 prep: build the five J01 axis candidates, prove the Pot J corpus is the exact
# Ticket 13 T09_ALL one, stage five 12-file axis packs, then submit the 10-cell array and
# its report job.  Runs on a compute node (the selector is heavy); the array it submits
# reuses the pinned Hierarchy-T13 binary, the t09 J02..J12 axes and every t09 breakline.
set -euo pipefail

RUN=${SLURM_SUBMIT_DIR:?}
WORK=$RUN/work/t16
PY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3
TREE=/data/gpfs/projects/punim2657/SfSpp/runs/20261125-1451_a50f8cc_t09-potJ/trees/J_K3R1/J/MM
T09_AX=/data/gpfs/projects/punim2657/SfSpp/runs/20261125-1340_a50f8cc_t09-own-surfaces/out/axes09_own_regen
SRC_EXE=/data/gpfs/projects/punim2657/SfSpp/runs/20261122-1612_651fee0_t13-j01-recip/work/build/Hierarchy-T13
WANT_SHA=de44ffc23c8db5208bd5f6f9c9f57d819bed7805f0330526bcb2750487bfd727
POSE_SHA=1d06dd60
STEM=Pot_J_Piece_01
ARMS="CTL_T09_WITH_AUTHOR_J01 OWN_NO_HANDLE_SHIP OWN_NO_HANDLE_THICKSEC OWN_VOXEL_THICKSEC OWN_S0_ONLY_SHIP"
STATUS=$RUN/logs/run_status.txt
PANEL=$RUN/panel

mkdir -p "$RUN"/logs "$RUN"/evidence "$RUN"/axes16 "$RUN"/axes16_packs "$RUN"/out \
         "$RUN"/score "$RUN"/renders "$RUN"/work "$RUN"/panel/build "$RUN"/panel/logs \
         "$RUN"/tmp
utc() { date -u +%Y-%m-%dT%H:%M:%SZ; }
say() { echo "$*" | tee -a "$STATUS"; }
say "prep-start $(utc) job=$SLURM_JOB_ID host=$(hostname) run=$RUN"

# ---- pinned assembler -------------------------------------------------------------
ln -f "$SRC_EXE" "$PANEL/build/Hierarchy-T13"
GOT_SHA=$(sha256sum "$PANEL/build/Hierarchy-T13" | awk '{print $1}')
if [ "$GOT_SHA" != "$WANT_SHA" ]; then
  say "[PANEL] FAIL exe_sha=$GOT_SHA want=$WANT_SHA"; exit 11
fi
echo "$WANT_SHA  /panel/build/Hierarchy-T13" > "$PANEL/logs/executable.sha256"
say "[PANEL] exe_sha=$GOT_SHA (WANT_SHA match)"

if [ ! -f "$WORK/posecheck13.sh" ]; then say "[POSE] FAIL posecheck13.sh missing"; exit 12; fi
POSE_FULL=$(sha256sum "$WORK/posecheck13.sh" | awk '{print $1}')
say "[POSE] posecheck13.sh sha256=$POSE_FULL (t13 recorded prefix $POSE_SHA)"

# ---- corpus identity --------------------------------------------------------------
if ! "$PY" "$WORK/verify_tree16.py" --run "$RUN" --tree "$TREE" >> "$RUN/logs/prep16_tree.log" 2>&1; then
  say "[CORPUS] FAIL manifest/axis pins (see logs/prep16_tree.log)"; exit 13
fi
PINLINES=$(( $(wc -l < "$RUN/logs/tree_pins16.tsv") - 1 ))
say "[CORPUS] manifest rows=$PINLINES axes=12 all-identical (logs/axis_pins16.tsv)"

# ---- five J01 axis candidates -----------------------------------------------------
set +e
"$PY" "$WORK/prep_j01_axes16.py" --run "$RUN" > "$RUN/logs/prep16_axes.log" 2>&1
AXRC=$?
set -e
say "[AXES] prep_j01_axes16.py rc=$AXRC"
if [ $AXRC -ne 0 ] || ! grep -q 'T16-AXES-OK$' "$RUN/logs/prep16_axes.log"; then
  say "[AXES] FAIL (see logs/prep16_axes.log)"; exit 14
fi
grep '^\[t16\]' "$RUN/logs/prep16_axes.log" >> "$STATUS" || true
AXROWS=$(($(wc -l < "$RUN/evidence/j01_axes16.tsv") - 1))
if [ "$AXROWS" -ne 5 ]; then say "[AXES] FAIL rows=$AXROWS want=5"; exit 15; fi

# ---- stage five axis packs: J02..J12 from t09, J01 from the arm --------------------
printf 'arm\taxes\toverwritten\n' > "$RUN/logs/axis_diff16.tsv"
for ARM in $ARMS; do
  PACK=$RUN/axes16_packs/$ARM
  rm -rf "$PACK"; mkdir -p "$PACK/Axes"
  cp "$T09_AX"/Pot_J_Piece_*_Axis.xyz "$PACK/Axes/"
  cp "$RUN/axes16/$ARM/${STEM}_Axis.xyz" "$PACK/Axes/"
  N=$(ls "$PACK/Axes"/*_Axis.xyz | wc -l)
  D=$(cd "$PACK/Axes" && for f in *_Axis.xyz; do
        if [ "$f" = "${STEM}_Axis.xyz" ]; then continue; fi
        if ! cmp -s "$f" "$T09_AX/$f"; then echo "$f"; fi
      done | wc -l)
  if [ "$N" -ne 12 ] || [ "$D" -ne 0 ]; then
    say "[STAGE] FAIL arm=$ARM files=$N changed_non_j01=$D"; exit 16
  fi
  printf '%s\t%d\t%s\n' "$ARM" "$N" "${STEM}_Axis.xyz" >> "$RUN/logs/axis_diff16.tsv"
  say "[STAGE] arm=$ARM axes=12 changed_non_j01=0"
done

# ---- submit -----------------------------------------------------------------------
printf 'idx\tarm\trep\taxis_dir\n' > "$RUN/logs/array_map.tsv"
IDX=0
for ARM in $ARMS; do
  for REP in 1 2; do
    printf '%d\t%s\t%d\t%s\n' "$IDX" "$ARM" "$REP" "$RUN/axes16_packs/$ARM/Axes" >> "$RUN/logs/array_map.tsv"
    IDX=$((IDX + 1))
  done
done
SB=$(sbatch --parsable --array=0-9%3 "$WORK/run_potj16.sbatch")
RB=$(sbatch --parsable --dependency=afterany:"$SB" "$WORK/run_potj16.sbatch" REPORT report)
echo "$SB" > "$RUN/logs/array_job.txt"
echo "$RB" > "$RUN/logs/report_job.txt"
say "[SUBMIT] array=$SB report=$RB"
printf 'parent\tid\n' > "$RUN/logs/parent_jobs.tsv"
printf 'array\t%s\n' "$SB" >> "$RUN/logs/parent_jobs.tsv"
printf 'report\t%s\n' "$RB" >> "$RUN/logs/parent_jobs.tsv"
"$PY" - "$RUN" "$SLURM_JOB_ID" "$SB" "$RB" <<'PYEOF'
import json, os, sys
run, prep_id, array_id, report_id = sys.argv[1:5]
json.dump({"run": run, "prep_job": prep_id, "array_job": array_id,
           "report_job": report_id, "status": "submitted"},
          open(os.path.join(run, "logs", "prep_status.json"), "w"), indent=1)
PYEOF
say "prep-done $(utc) array=$SB report=$RB"
