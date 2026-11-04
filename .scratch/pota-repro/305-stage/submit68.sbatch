#!/bin/bash
#SBATCH --job-name=t68-jug-axes
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=02:00:00
#SBATCH --output=logs/slurm-%j.out
#SBATCH --error=logs/slurm-%j.err
#
# submit68.sbatch -- ticket 68 Part A: the t67 F20 panel (guarded shim, floor 20, t66 arm-U lanes)
# with the nine Juglet axis files SUBSTITUTED by the t68 hybrid set ($RUN/axes68/, ticket-301 way:
# only the Axes/ dir of a copy of the staged tree differs). F20O = old axes, same job, as baseline.
# Submitted FROM the run dir (RUN=$SLURM_SUBMIT_DIR). Derived from t67's submit67.sbatch.
# Every binary is compiled from a COPY under work/shim/; nothing is merged into any checkout.
# The job appends NO index.tsv row (verdict / human_note belong to the lead).
set -uo pipefail

RUN=$SLURM_SUBMIT_DIR
LANES=/data/gpfs/projects/punim2657/SfSpp/runs/20261103-1332_fab76f5_t66-admitsign-default/outU_jug/geom
T58=/data/gpfs/projects/punim2657/SfSpp/runs/20261101-1913_d8f716f_t58-floor-density-panel
DS=/data/gpfs/projects/punim2657/sfs_preprocessing/Dataset
POTA=/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp
MAIN=/data/gpfs/projects/punim2657/sfs_main
SIF=$MAIN/sfs_pristine_assembly.sif
APT=/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer
PY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3
SHIPPED=$MAIN/sfspreproc-docker/hpc/tools/main_pristine_batch.cpp
WORK=$RUN/work
OUT=$RUN/out
TREES=$RUN/trees
LOG=$RUN/logs
INS=$RUN/instruments
GT="$TREES/juglet/Ground Truth"

mkdir -p $WORK/inc1/class $WORK/inc2/class $WORK/shim $WORK/logs $OUT $TREES $LOG $RUN/score
cp $INS/arm67.sh $WORK/arm67.sh
chmod +x $WORK/arm67.sh

echo "=== t68 job $SLURM_JOB_ID on $(hostname) at $(date -u +%FT%TZ)"
echo "=== run dir $RUN"

{
  echo "jobid $SLURM_JOB_ID"
  date -u +%FT%TZ
  echo "--- shipped shim"
  md5sum $SHIPPED
  echo "--- SIF"
  ls -l $SIF
  echo "--- instruments"
  md5sum $INS/*
  echo "--- t66 arm-U lanes, READ-ONLY input"
  md5sum $LANES/Juglet_Piece_*.Bl0 $LANES/Juglet_Piece_*.S0 $LANES/Juglet_Piece_*.S1
  echo "--- sfs_main checkout"
  git -C $MAIN/sfspreproc-docker rev-parse HEAD origin/main
  git -C $MAIN/sfspreproc-docker status --porcelain | head
} > $LOG/provenance.log 2>&1

# ---------- guarded base shim (refuses unless both anchors occur exactly once) ----------
$PY $INS/patch_guard67.py $SHIPPED $WORK/shim/G.cpp > $LOG/guard.log 2>&1
GRC=$?
diff -u $SHIPPED $WORK/shim/G.cpp > $LOG/diff_guard.txt
md5sum $SHIPPED $WORK/shim/G.cpp >> $LOG/guard.log
cat $LOG/guard.log
if [ $GRC -ne 0 ]; then echo "!!!! guard patch failed rc=$GRC"; exit 4; fi

# ---------- include roots: t58's recipe, JUGLET_ORIG block copied from the t58 run ----------
$APT exec $SIF cat /opt/sfs-pristine/class/data_path.h > $WORK/inc2/class/data_path.h 2>>$LOG/provenance.log
cp $WORK/inc2/class/data_path.h $WORK/inc1/class/data_path.h
sed -i 's/^#define POT_A$/#define POT_A_INFRA_OFF_JUGLET/' $WORK/inc1/class/data_path.h
cp $T58/work/juglet_orig_block.inc $WORK/juglet_orig_block.inc
echo "BLOCK_MD5 $(md5sum $WORK/juglet_orig_block.inc | cut -d' ' -f1)  expect 401195eae5a41579563fc237a9843298" >> $LOG/provenance.log
cat $WORK/juglet_orig_block.inc >> $WORK/inc1/class/data_path.h
grep -n '^#define POT_A\|^#define POT_A_INFRA\|^#define JUGLET_ORIG_BASE' $WORK/inc1/class/data_path.h $WORK/inc2/class/data_path.h >> $LOG/provenance.log 2>&1
grep BLOCK_MD5 $LOG/provenance.log

# ---------- stage -----------------------------------------------------------
$PY $INS/stage67_inputs.py --lanes $LANES --dataset $DS --pota $POTA --out $TREES > $LOG/stage.log 2>&1
echo "stage rc=$?" >> $LOG/stage.log
cat $LOG/stage.log

# ---------- axis substitution: copy of the staged Juglet tree, only Axes/ replaced ----------
rm -rf $TREES/juglet_ax68
cp -r $TREES/juglet $TREES/juglet_ax68
cp -f $RUN/axes68/Juglet_Piece_?_Axis.xyz $TREES/juglet_ax68/Axes/
{
  echo "--- axes: staged old (from \$DS) vs substituted t68 hybrid"
  md5sum $TREES/juglet/Axes/*.xyz $TREES/juglet_ax68/Axes/*.xyz
  echo "--- trees differ only in Axes/ (expect 9 'differ' lines, all under Axes/):"
  diff -rq $TREES/juglet $TREES/juglet_ax68
} > $LOG/axes_subst.log 2>&1
cat $LOG/axes_subst.log
NDIFF=$(diff -rq $TREES/juglet $TREES/juglet_ax68 | wc -l)
NAX=$(diff -rq $TREES/juglet $TREES/juglet_ax68 | grep -c '/Axes/')
if [ "$NDIFF" -ne 9 ] || [ "$NAX" -ne 9 ]; then echo "!!!! substitution not axes-only ($NDIFF / $NAX)"; exit 5; fi

# ---------- arms ------------------------------------------------------------
printf 'arm\tfloor\tinc\ttree\tnp\textra\texit\twall_s\n' > $LOG/panel.tsv
runarm () {
  ARM=$1; FLOOR=$2; INC=$3; TREE=$4; NP=$5; EXTRA=$6
  T0=$SECONDS
  echo "##### LAUNCH $ARM floor=$FLOOR tree=$TREE"
  $APT exec --writable-tmpfs \
     --bind $MAIN:/workspace --bind $WORK:/panel --bind $OUT:/out --bind $TREE:/Dataset/SfS_pp \
     $SIF bash /panel/arm67.sh $ARM $FLOOR $INC $NP $EXTRA >> $LOG/panel.log 2>&1
  RC=$?
  DT=$((SECONDS - T0))
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$ARM" "$FLOOR" "$INC" "$TREE" "$NP" "$EXTRA" "$RC" "$DT" >> $LOG/panel.tsv
  echo "##### $ARM exit=$RC wall=$DT sec"
  return 0
}

runarm F20O  20 /panel/inc1 $TREES/juglet      9 -DJUGLET_ORIG
runarm F20N  20 /panel/inc1 $TREES/juglet_ax68 9 -DJUGLET_ORIG

echo "--- variant sources and binaries:"
md5sum $WORK/shim/*.cpp $WORK/build/Hierarchy-* 2>/dev/null | tee $LOG/md5_binaries.txt
cp $WORK/logs/* $LOG/ 2>/dev/null
cat $LOG/panel.tsv

# ---------- score (t58's scorer; its 36/18 denominators are right only for all-9-active arms) ----------
for ARM in F20O F20N; do
  $PY $T58/instruments/score58.py --result $OUT/$ARM --gt "$GT" \
      --mesh "$TREES/juglet/Mesh" --lanes "$TREES/juglet/Breaklines" \
      --out $RUN/score/$ARM.json --label $ARM > $RUN/score/$ARM.stdout 2> $RUN/score/$ARM.stderr
  echo "score $ARM rc=$?"
done
for ARM in F20O F20N; do echo "[$ARM]"; cat "$OUT/$ARM/1. Acc.txt" 2>/dev/null; done

echo "=== t68 job finished $(date -u +%FT%TZ)"
