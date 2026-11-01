#!/bin/bash
#SBATCH --job-name=t58-panel
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=04:00:00
#SBATCH --output=logs/slurm-%j.out
#SBATCH --error=logs/slurm-%j.err
#
# run_panel_t58.sbatch -- ticket 58 floor / density panel (ONE Slurm job, 7 arms).
# Every arm compiles its OWN experimental binary from a sed-ed COPY of the shipped shim
# (md5 + diff recorded in the arm log); no variant is ever merged into any checkout.
# The job appends NO index.tsv row (verdict / human_note belong to the lead).
#
# prior_attempt jobid 34175087 failed after 6 s: (a) GT=$TREES/juglet/Ground Truth split on
# the space in 'Ground Truth'; (b) arm.sh was never copied under the /panel bind.
set -uo pipefail

RUN=/data/gpfs/projects/punim2657/SfSpp/runs/20261101-1913_d8f716f_t58-floor-density-panel
T55=/data/gpfs/projects/punim2657/SfSpp/runs/20261101-2004_05be12c_t55-worness07-breaklines/out/geom
DS=/data/gpfs/projects/punim2657/sfs_preprocessing/Dataset
POTA=/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp
MAIN=/data/gpfs/projects/punim2657/sfs_main
SIF=$MAIN/sfs_pristine_assembly.sif
APT=/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer
PY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3
SHIM=$MAIN/sfspreproc-docker/hpc/tools/main_pristine_batch.cpp
WORK=$RUN/work
OUT=$RUN/out
TREES=$RUN/trees
LOG=$RUN/logs
INS=$RUN/instruments
GT="$TREES/juglet/Ground Truth"

mkdir -p $WORK/inc1/class $WORK/inc2/class $WORK/shim $WORK/logs $OUT $TREES $LOG $RUN/score
cp $INS/arm.sh $WORK/arm.sh
chmod +x $WORK/arm.sh

echo "=== t58 panel job $SLURM_JOB_ID on $(hostname) at $(date -u +%FT%TZ)"
echo "=== run dir $RUN"
echo "=== GT dir [$GT]"
ls "$GT"

# ---------- provenance -------------------------------------------------------
{
  echo "jobid $SLURM_JOB_ID"
  date -u +%FT%TZ
  echo "--- shim source (the file every variant is sed-ed from)"
  md5sum $SHIM
  echo "--- SIF"
  ls -l $SIF
  echo "--- instruments"
  md5sum $INS/*.py $INS/*.sh $INS/*.sbatch
  echo "--- t55 run of record, READ-ONLY input"
  md5sum $T55/*
  echo "--- Pot A bundle (hardlinked, never written)"
  ls -l $POTA/Breaklines/Pot_A_Piece_01_Breakline_0.pcd
  echo "--- sfs_main checkout"
  git -C $MAIN/sfspreproc-docker rev-parse origin/main
  git -C $MAIN/sfspreproc-docker status --porcelain | head
  echo "--- index.tsv line count (this job appends nothing)"
  wc -l /data/gpfs/projects/punim2657/SfSpp/runs/index.tsv
} > $LOG/provenance.log 2>&1

# ---------- include roots ----------------------------------------------------
$APT exec $SIF cat /opt/sfs-pristine/class/data_path.h > $WORK/inc2/class/data_path.h 2>>$LOG/provenance.log
cp $WORK/inc2/class/data_path.h $WORK/inc1/class/data_path.h
sed -i 's/^#define POT_A$/#define POT_A_INFRA_OFF_JUGLET/' $WORK/inc1/class/data_path.h
git -C $MAIN/sfspreproc-docker show origin/main:class/data_path.h | sed -n "1715,1820p" > $WORK/juglet_orig_block.inc
echo "BLOCK_MD5 $(md5sum $WORK/juglet_orig_block.inc | cut -d' ' -f1)  expect 401195eae5a41579563fc237a9843298" >> $LOG/provenance.log
cat $WORK/juglet_orig_block.inc >> $WORK/inc1/class/data_path.h
echo "--- inc1 actives:" >> $LOG/provenance.log
grep -n '^#define POT_A\|^#define POT_A_INFRA\|^#define JUGLET_ORIG_BASE' $WORK/inc1/class/data_path.h >> $LOG/provenance.log 2>&1
echo "--- inc2 actives:" >> $LOG/provenance.log
grep -n '^#define POT_A\|^#define POT_A_INFRA\|^#define JUGLET_ORIG_BASE' $WORK/inc2/class/data_path.h >> $LOG/provenance.log 2>&1
head -14 $LOG/provenance.log

# ---------- stage the input trees -------------------------------------------
$PY $INS/stage_inputs.py --t55 $T55 --dataset $DS --pota $POTA --out $TREES --interp-dots 60 > $LOG/stage.log 2>&1
echo "stage_inputs rc=$?" >> $LOG/stage.log
tail -3 $LOG/stage.log

# ---------- run the arms -----------------------------------------------------
printf 'arm\tfloor\tinc\ttree\tnp\textra\texit\twall_s\n' > $LOG/panel.tsv
runarm () {
  ARM=$1; FLOOR=$2; INC=$3; TREE=$4; NP=$5; EXTRA=$6
  T0=$SECONDS
  echo "##### LAUNCH $ARM floor=$FLOOR inc=$INC tree=$TREE np=$NP extra=$EXTRA"
  $APT exec --writable-tmpfs \
     --bind $MAIN:/workspace --bind $WORK:/panel --bind $OUT:/out --bind $TREE:/Dataset/SfS_pp \
     $SIF bash /panel/arm.sh $ARM $FLOOR $INC $NP $EXTRA >> $LOG/panel.log 2>&1
  RC=$?
  DT=$((SECONDS - T0))
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$ARM" "$FLOOR" "$INC" "$TREE" "$NP" "$EXTRA" "$RC" "$DT" >> $LOG/panel.tsv
  echo "##### $ARM exit=$RC wall=$DT sec"
  return 0
}

runarm F50  50 /panel/inc1 $TREES/juglet     9 -DJUGLET_ORIG
runarm F45  45 /panel/inc1 $TREES/juglet     9 -DJUGLET_ORIG
runarm F10  10 /panel/inc1 $TREES/juglet     9 -DJUGLET_ORIG
runarm F0    0 /panel/inc1 $TREES/juglet     9 -DJUGLET_ORIG
runarm F10R 10 /panel/inc1 $TREES/juglet     9 -DJUGLET_ORIG
runarm I60  50 /panel/inc1 $TREES/juglet_n60 9 -DJUGLET_ORIG
runarm PA10 10 /panel/inc2 $TREES/pota       8 NONE

echo "--- variant md5s (the experimental binaries):"
md5sum $WORK/shim/*.cpp 2>/dev/null
ls -l $WORK/build/Hierarchy-* 2>/dev/null
md5sum $WORK/build/Hierarchy-* 2>/dev/null

# ---------- score ------------------------------------------------------------
scorearm () {
  ARM=$1; LANES=$2
  $PY $INS/score58.py --result $OUT/$ARM --gt "$GT" \
      --mesh "$TREES/juglet/Mesh" --lanes "$LANES" \
      --out $RUN/score/$ARM.json --label $ARM > $RUN/score/$ARM.stdout 2> $RUN/score/$ARM.stderr
  echo "score $ARM rc=$?"
}
scorearm F50  "$TREES/juglet/Breaklines"
scorearm F45  "$TREES/juglet/Breaklines"
scorearm F10  "$TREES/juglet/Breaklines"
scorearm F0   "$TREES/juglet/Breaklines"
scorearm F10R "$TREES/juglet/Breaklines"
scorearm I60  "$TREES/juglet_n60/Breaklines"

# ---------- determinism proof: F10 vs F10R -----------------------------------
snap () {
  D=$1
  for i in 1 2 3 4 5 6 7 8 9; do
    for kind in Edgeline OBJ; do
      f=$(ls $D/*_"$kind"_"$i".* 2>/dev/null | head -1)
      if [ -n "$f" ]; then echo "$kind $i $(md5sum $f | cut -d' ' -f1)"; fi
    done
  done
  for i in 0 1 2 3 4 5 6 7 8; do
    f=$D/T_"$i"to_"$i".txt
    if [ -f "$f" ]; then echo "T $i $(md5sum $f | cut -d' ' -f1)"; fi
  done
}
{
  echo "--- binary logs"
  md5sum $LOG/binary_F10.log $LOG/binary_F10R.log 2>/dev/null
  echo "--- result snapshot content (name-normalised)"
  snap $OUT/F10  > $LOG/snap_F10.txt
  snap $OUT/F10R > $LOG/snap_F10R.txt
  cat $LOG/snap_F10.txt
  if diff $LOG/snap_F10.txt $LOG/snap_F10R.txt > /dev/null; then echo "SNAPSHOT CONTENT IDENTICAL"; else echo "SNAPSHOT DIFFERS"; diff $LOG/snap_F10.txt $LOG/snap_F10R.txt; fi
  echo "--- Acc.txt side by side"
  echo "[F10]";  cat "$OUT/F10/1. Acc.txt" 2>/dev/null
  echo "[F10R]"; cat "$OUT/F10R/1. Acc.txt" 2>/dev/null
  echo "--- Pot A regression control Acc.txt"
  cat "$OUT/PA10/1. Acc.txt" 2>/dev/null
} > $LOG/determinism.log 2>&1
cat $LOG/determinism.log

echo "=== panel finished $(date -u +%FT%TZ)"
