#!/bin/bash
#SBATCH --job-name=t328e2e
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=64G
#SBATCH --time=01:30:00
#
# Ticket 328 bar 4: Juglet E2E, GT-axes arm, two repeats of the cured lanes + one shipped-lane
# control repeat. Template = runs/20261110-0320_41494d0_t320b-juglet/submit.sbatch verbatim except:
#   * the lanes are this ticket's cured geom (job D outgt_jug/geom) and t66's outU_jug/geom;
#   * every tree's Axes/ is overwritten with Dataset/Juglet_GT (GT-axes arm), so the only
#     difference between the arms is the breakline/surface geometry;
#   * the seam gate is untouched.
set -uo pipefail

RUN=$SLURM_SUBMIT_DIR
CURED=${CURED:?set CURED to the cured geom dir (job D outgt_jug/geom)}
SHIPPED_LANES=/data/gpfs/projects/punim2657/SfSpp/runs/20261103-1332_fab76f5_t66-admitsign-default/outU_jug/geom
DS=/data/gpfs/projects/punim2657/sfs_preprocessing/Dataset
GT=$DS/Juglet_GT
CORP=/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp
MAIN=/data/gpfs/projects/punim2657/sfs_main
SIF=$MAIN/sfs_pristine_assembly.sif
APT=/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer
PY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3
SHIPPED=$MAIN/sfspreproc-docker/hpc/tools/main_pristine_batch.cpp
BLOCK=/data/gpfs/projects/punim2657/SfSpp/runs/20261101-1913_d8f716f_t58-floor-density-panel/work/juglet_orig_block.inc

WORK=$RUN/work
TREES=$RUN/trees
OUT=$RUN/out
SC=$RUN/score
FLOOR=20
NP=9
JOBID=${SLURM_JOB_ID:-na}

fail() { echo "RUN-FAILED: $*" | tee "$RUN/RUN-FAILED.txt"; exit "${2:-1}"; }

for v in $(compgen -e | grep -E "^(SFS_|POT_NAME$)"); do unset "$v"; done
cd "$RUN" || exit 1
mkdir -p "$WORK/inc_src/class" "$WORK/shim" "$OUT" "$TREES" "$SC" logs

echo "[JOB] runid=$(basename "$RUN") job=$JOBID start=$(date -u +%FT%TZ) cured=$CURED"

# corpus listing BEFORE (read-only proof for bar 5)
{ echo "== DS $DS"; find "$DS" -maxdepth 3 -type f | LC_ALL=C sort | head -500 | xargs -r md5sum 2>/dev/null | head -500
  echo "== CORP $CORP"; find "$CORP" -maxdepth 3 -type f | LC_ALL=C sort | head -500 | xargs -r md5sum 2>/dev/null | head -500
} > "$RUN/list_corpus_before.txt" 2>&1

# ---- guarded base + juglet include block
$PY "$WORK/patch_guard67.py" "$SHIPPED" "$WORK/shim/G.cpp" > logs/guard.log 2>&1 || fail 4 "patch_guard67 failed"
$APT exec "$SIF" cat /opt/sfs-pristine/class/data_path.h > "$WORK/inc_src/class/data_path.h" 2>>logs/provenance.log || fail 5 "cannot read pristine data_path.h"
mkdir -p "$WORK/inc_jug/class"
$PY "$WORK/mk_inc.py" "$WORK/inc_src/class/data_path.h" "$WORK/inc_jug/class/data_path.h" NONE --append "$BLOCK" > logs/mk_inc.log 2>&1 || fail 6 "mk_inc failed"

# ---- stage the two lane sets
$PY "$WORK/stage67_inputs.py" --lanes "$CURED"        --dataset "$DS" --pota "$CORP" --out "$WORK/stage_cured"   > logs/stage_cured.log   2>&1 || fail 7 "stage cured failed"
$PY "$WORK/stage67_inputs.py" --lanes "$SHIPPED_LANES" --dataset "$DS" --pota "$CORP" --out "$WORK/stage_shipped" > logs/stage_shipped.log 2>&1 || fail 7 "stage shipped failed"

# ---- GT-axes arm: overwrite Axes with Dataset/Juglet_GT, then two repeats of the cured tree + one control
for t in cured shipped; do
  for i in $(seq 1 9); do
    cp -f "$GT/Juglet_Piece_${i}_Axis.xyz" "$WORK/stage_$t/juglet/Axes/Juglet_Piece_${i}_Axis.xyz" || fail 8 "GT axis copy failed"
  done
done
rm -rf "$TREES"/juglet_*
cp -a "$WORK/stage_cured/juglet"   "$TREES/juglet_cured_r1"
cp -a "$WORK/stage_cured/juglet"   "$TREES/juglet_cured_r2"
cp -a "$WORK/stage_shipped/juglet" "$TREES/juglet_shipped_r1"
for t in "$TREES"/juglet_*; do
  ( cd "$t" && find . -type f -o -type l | LC_ALL=C sort | xargs -r md5sum ) > "$(dirname "$t")/$(basename "$t").md5"
done

# ---- warm build
$APT exec --writable-tmpfs \
   --bind /data/gpfs:/data/gpfs --bind "$MAIN":/workspace --bind "$WORK":/panel \
   "$SIF" bash -c '
     mkdir -p /panel/build /panel/logs
     cd /panel/build
     cmake /opt/sfs-pristine -DCMAKE_BUILD_TYPE=Release > /panel/logs/cmake.log 2>&1
     make -j8 > /panel/logs/make.log 2>&1
   ' || fail 9 "pristine object build failed"

export OMP_NUM_THREADS=4
runarm() {
  local LABEL=$1 TREE=$2
  local T0=$SECONDS
  echo "##### LAUNCH $LABEL tree=$TREE $(date -u +%FT%TZ)"
  $APT exec --writable-tmpfs \
     --bind /data/gpfs:/data/gpfs --bind "$MAIN":/workspace --bind "$WORK":/panel --bind "$OUT":/out --bind "$TREE":/Dataset/SfS_pp \
     "$SIF" bash /panel/arm67.sh "$LABEL" "$FLOOR" /panel/inc_jug "$NP" -DJUGLET_ORIG > "logs/run_${LABEL}.log" 2>&1
  local RC=$? DT=$((SECONDS - T0))
  printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\n" "$LABEL" "$FLOOR" /panel/inc_jug "$TREE" "$NP" "$RC" "$DT" > "logs/panel_${LABEL}.row"
  echo "##### DONE $LABEL exit=$RC wall=${DT}s $(date -u +%FT%TZ)"
  if [ -d "$OUT/$LABEL" ]; then
    $PY "$WORK/acc305.py" "$OUT/$LABEL" "$LABEL" "$SC/acc_${LABEL}.row" >> "logs/acc_${LABEL}.log" 2>&1
    [ -f "$OUT/$LABEL/1. Acc.txt" ] && cp -f "$OUT/$LABEL/1. Acc.txt" "$SC/$LABEL.Acc.txt"
    $PY "$WORK/score58.py" --result "$OUT/$LABEL" --gt "$GT" \
        --mesh "$TREE/Mesh" --lanes "$TREE/Breaklines" \
        --out "$SC/$LABEL.json" --label "$LABEL" > "logs/score_${LABEL}.log" 2>&1
  fi
}

runarm "T328C_r1" "$TREES/juglet_cured_r1"
runarm "T328C_r2" "$TREES/juglet_cured_r2"
runarm "T66O_r1"  "$TREES/juglet_shipped_r1"

printf "label\ttime_s\tsherd\tedge\traw\n" > "$SC/acc.tsv"
printf "arm\tfloor\tinc\ttree\tnp\texit\twall_s\n" > logs/panel.tsv
for arm in T328C_r1 T328C_r2 T66O_r1; do
  [ -f "logs/panel_${arm}.row" ] && cat "logs/panel_${arm}.row" >> logs/panel.tsv
  [ -f "$SC/acc_${arm}.row" ] && cat "$SC/acc_${arm}.row" >> "$SC/acc.tsv"
done
cat logs/panel.tsv
cat "$SC/acc.tsv"

# corpus listing AFTER (read-only proof)
{ echo "== DS $DS"; find "$DS" -maxdepth 3 -type f | LC_ALL=C sort | head -500 | xargs -r md5sum 2>/dev/null | head -500
  echo "== CORP $CORP"; find "$CORP" -maxdepth 3 -type f | LC_ALL=C sort | head -500 | xargs -r md5sum 2>/dev/null | head -500
} > "$RUN/list_corpus_after.txt" 2>&1
diff "$RUN/list_corpus_before.txt" "$RUN/list_corpus_after.txt" > "$RUN/list_corpus.diff" 2>&1 && echo "corpus listing identical" || echo "CORPUS LISTING CHANGED (see list_corpus.diff)"

echo "[JOB] complete at $(date -u +%FT%TZ)"
