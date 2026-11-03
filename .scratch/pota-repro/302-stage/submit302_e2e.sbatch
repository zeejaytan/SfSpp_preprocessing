#!/bin/bash
#SBATCH --job-name=t302-e2e
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=03:00:00
#SBATCH --output=logs/slurm-%j.out
#SBATCH --error=logs/slurm-%j.err
#
# Ticket 302 gate 4: assembler E2E with corrected axes.
#   juglet302.py first: corrected axes from t66 arm-U walls -> work/axes302_jug/
#   F20O  Juglet floor 20, Dataset axes (baseline = t67/t68 F20O)
#   F20N  Juglet floor 20, corrected port axes substituted (only Axes/ differs)
#   GPA50 Pot A floor 50, corpus axes (control, = guard68 GPA50)
#   GPA50N Pot A floor 50, corrected corpus axes (run 20261103-1612_...t302-corpus-axes)
# Derived from t68 submit.sbatch (guarded shim, apptainer SIF, score58).
# Appends NO index row. Read-only: corpus, Dataset, sfs_main, t66 lanes.
set -uo pipefail
STATUS_DIR=/data/gpfs/projects/punim2657/SfSpp/logs
mkdir -p "$STATUS_DIR"
trap 'rc=$?; echo "$(date -u +%FT%TZ) job $SLURM_JOB_ID exit $rc" >> "$STATUS_DIR/job_status.log"' EXIT
RUN=$SLURM_SUBMIT_DIR
CORPUSRUN=/data/gpfs/projects/punim2657/SfSpp/runs/20261103-1612_01bff01_t302-corpus-axes
LANES=/data/gpfs/projects/punim2657/SfSpp/runs/20261103-1332_fab76f5_t66-admitsign-default/outU_jug/geom
T58=/data/gpfs/projects/punim2657/SfSpp/runs/20261101-1913_d8f716f_t58-floor-density-panel
T68=/data/gpfs/projects/punim2657/SfSpp/runs/20261103-1523_4b516be_t68-axis-method
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
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
unset SFS_AXES_REFINE_NOOP

mkdir -p $WORK/inc1/class $WORK/inc2/class $WORK/shim $WORK/logs $OUT $TREES $LOG $RUN/score
cp $T68/instruments/arm67.sh $T68/instruments/stage67_inputs.py $T68/instruments/patch_guard67.py $INS/
cp $RUN/work/juglet302.py $INS/

echo "=== t302-e2e job $SLURM_JOB_ID on $(hostname) at $(date -u +%FT%TZ)"
{
  echo "--- corpus-axes run (dependency)"
  ls -l $CORPUSRUN/out/axes302/Pot_A_Piece_0?_Axis.xyz
  echo "--- shipped shim / SIF / instruments"
  md5sum $SHIPPED $INS/* $RUN/work/juglet302.py
  echo "--- t66 arm-U lanes (READ-ONLY input)"
  md5sum $LANES/Juglet_Piece_*.Bl0 $LANES/Juglet_Piece_*.S0 $LANES/Juglet_Piece_*.S1
  git -C $MAIN/sfspreproc-docker rev-parse HEAD origin/main
} > $LOG/provenance.log 2>&1

# ---------- corrected Juglet axes ----------
$PY $RUN/work/juglet302.py $LANES $DS $WORK/axes302_jug > $LOG/juglet302.log 2>&1
JRC=$?
echo "juglet302 rc=$JRC"
tail -14 $LOG/juglet302.log
[ $JRC -ne 0 ] && exit $JRC

# ---------- guarded base shim ----------
$PY $INS/patch_guard67.py $SHIPPED $WORK/shim/G.cpp > $LOG/guard.log 2>&1
GRC=$?
diff -u $SHIPPED $WORK/shim/G.cpp > $LOG/diff_guard.txt
md5sum $SHIPPED $WORK/shim/G.cpp >> $LOG/guard.log
cat $LOG/guard.log
if [ $GRC -ne 0 ]; then echo "!!!! guard patch failed rc=$GRC"; exit 4; fi

# ---------- include roots (t58/t68 recipe) ----------
$APT exec $SIF cat /opt/sfs-pristine/class/data_path.h > $WORK/inc2/class/data_path.h 2>>$LOG/provenance.log
cp $WORK/inc2/class/data_path.h $WORK/inc1/class/data_path.h
sed -i 's/^#define POT_A$/#define POT_A_INFRA_OFF_JUGLET/' $WORK/inc1/class/data_path.h
cp $T58/work/juglet_orig_block.inc $WORK/juglet_orig_block.inc
echo "BLOCK_MD5 $(md5sum $WORK/juglet_orig_block.inc | cut -d' ' -f1)  expect 401195eae5a41579563fc237a9843298" >> $LOG/provenance.log
cat $WORK/juglet_orig_block.inc >> $WORK/inc1/class/data_path.h

# ---------- stage trees ----------
$PY $INS/stage67_inputs.py --lanes $LANES --dataset $DS --pota $POTA --out $TREES > $LOG/stage.log 2>&1
echo "stage rc=$?"
cat $LOG/stage.log | tail -3

# ---------- axis substitution (copies of staged trees, only Axes/ differs) ----------
rm -rf $TREES/juglet_ax302 $TREES/pota_ax302
cp -r $TREES/juglet $TREES/juglet_ax302
cp -r $TREES/pota $TREES/pota_ax302
cp -f $WORK/axes302_jug/Juglet_Piece_?_Axis.xyz $TREES/juglet_ax302/Axes/
cp -f $CORPUSRUN/out/axes302/Pot_A_Piece_0?_Axis.xyz $TREES/pota_ax302/Axes/
{
  md5sum $TREES/juglet/Axes/*.xyz $TREES/juglet_ax302/Axes/*.xyz
  md5sum $TREES/pota/Axes/*.xyz $TREES/pota_ax302/Axes/*.xyz
  echo "--- juglet diff (expect 9, all Axes/):"; diff -rq $TREES/juglet $TREES/juglet_ax302
  echo "--- pota diff (expect 8, all Axes/):"; diff -rq $TREES/pota $TREES/pota_ax302
} > $LOG/axes_subst.log 2>&1
cat $LOG/axes_subst.log
NDJ=$(diff -rq $TREES/juglet $TREES/juglet_ax302 | wc -l); NAJ=$(diff -rq $TREES/juglet $TREES/juglet_ax302 | grep -c '/Axes/')
NDP=$(diff -rq $TREES/pota $TREES/pota_ax302 | wc -l); NAP=$(diff -rq $TREES/pota $TREES/pota_ax302 | grep -c '/Axes/')
if [ "$NDJ" -ne 9 ] || [ "$NAJ" -ne 9 ] || [ "$NDP" -ne 8 ] || [ "$NAP" -ne 8 ]; then
  echo "!!!! substitution not axes-only ($NDJ/$NAJ $NDP/$NAP)"; exit 5
fi

# ---------- arms ----------
cp $INS/arm67.sh $WORK/arm67.sh
chmod +x $WORK/arm67.sh
printf 'arm\tfloor\tinc\ttree\tnp\textra\texit\twall_s\n' > $LOG/panel.tsv
runarm () {
  ARM=$1; FLOOR=$2; INC=$3; TREE=$4; NP=$5; EXTRA=$6
  T0=$SECONDS
  echo "##### LAUNCH $ARM floor=$FLOOR tree=$TREE"
  $APT exec --writable-tmpfs \
     --bind $MAIN:/workspace --bind $WORK:/panel --bind $OUT:/out --bind $TREE:/Dataset/SfS_pp \
     $SIF bash /panel/arm67.sh $ARM $FLOOR $INC $NP $EXTRA >> $LOG/panel.log 2>&1
  RC=$?
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$ARM" "$FLOOR" "$INC" "$TREE" "$NP" "$EXTRA" "$RC" "$((SECONDS - T0))" >> $LOG/panel.tsv
  echo "##### $ARM exit=$RC wall=$((SECONDS - T0)) sec"
  return 0
}

runarm F20O   20 /panel/inc1 $TREES/juglet      9 -DJUGLET_ORIG
runarm F20N   20 /panel/inc1 $TREES/juglet_ax302 9 -DJUGLET_ORIG
runarm GPA50  50 /panel/inc2 $TREES/pota        8 NONE
runarm GPA50N 50 /panel/inc2 $TREES/pota_ax302  8 NONE

md5sum $WORK/shim/*.cpp $WORK/build/Hierarchy-* 2>/dev/null | tee $LOG/md5_binaries.txt
cp $WORK/logs/* $LOG/ 2>/dev/null
cat $LOG/panel.tsv

# ---------- score (juglet arms; t58 scorer) ----------
for ARM in F20O F20N; do
  $PY $T58/instruments/score58.py --result $OUT/$ARM --gt "$GT" \
      --mesh "$TREES/juglet/Mesh" --lanes "$TREES/juglet/Breaklines" \
      --out $RUN/score/$ARM.json --label $ARM > $RUN/score/$ARM.stdout 2> $RUN/score/$ARM.stderr
  echo "score $ARM rc=$?"
done
for ARM in F20O F20N GPA50 GPA50N; do echo "[$ARM]"; cat "$OUT/$ARM/1. Acc.txt" 2>/dev/null; done
echo "=== t302-e2e finished $(date -u +%FT%TZ)"
