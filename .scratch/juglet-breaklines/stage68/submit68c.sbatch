#!/bin/bash
#SBATCH --job-name=t68c-densify
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=04:00:00
#SBATCH --output=logs/slurm-%j.out
#SBATCH --error=logs/slurm-%j.err
#
# submit68c.sbatch -- ticket 68 job 2: per-pair instrument + Part C densify arm. Submitted FROM the run dir.
#   I20N   : t67 attitude instrument (patch_attitude67.py on the guarded shim), floor 20, t66 arm-U lanes,
#            axes68 substituted -- the F20N arm's exact inputs, with the per-candidate replay.
#   D190   : edgeline cell, t66 recipe (worness 0.7, radius 1.0, admit-sign default on, mesh stage on the
#            Dataset axes exactly as t66), stock RESAMPLE_D_MM 1.9 -> run-to-run control (mesh stage RNG).
#   D095   : the same cell with RESAMPLE_D_MM = 0.95 (edgeline_extraction_headless.cpp:556, one literal).
#   I20_D190 / I20_D095 : instrumented floor-20 panel on those lanes, axes68 substituted.
# Corpus read-only. The job appends no index.tsv row and writes nothing outside the run dir.
set -uo pipefail
: "${NEW:?}"

RUN=$SLURM_SUBMIT_DIR
RUNID=$(basename $RUN)
JOBID=${SLURM_JOB_ID:-na}
P=${SLURM_CPUS_PER_TASK:-8}
LANES66=/data/gpfs/projects/punim2657/SfSpp/runs/20261103-1332_fab76f5_t66-admitsign-default/outU_jug/geom
T58=/data/gpfs/projects/punim2657/SfSpp/runs/20261101-1913_d8f716f_t58-floor-density-panel
CANON=/data/gpfs/projects/punim2657/sfs_preprocessing
DS=$CANON/Dataset
CORP=/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp
POTA=$CORP
MAIN=/data/gpfs/projects/punim2657/sfs_main
ASIF=$MAIN/sfs_pristine_assembly.sif
SIF=$CANON/pcl_191_nurbs.sif
APT=/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer
PY=/data/gpfs/projects/punim2657/TORA/envs/tora/bin/python3
SHIPPED=$MAIN/sfspreproc-docker/hpc/tools/main_pristine_batch.cpp
WORK=$RUN/work; OUT=$RUN/out; TREES=$RUN/trees; LOG=$RUN/logs; INS=$RUN/instruments
for v in $(compgen -e | grep -E '^(SFS_|POT_NAME$)'); do unset "$v"; done
mkdir -p $WORK/inc1/class $WORK/shim $WORK/logs $OUT $TREES $LOG $RUN/score
cp $INS/arm67.sh $WORK/arm67.sh

echo "=== t68c job $JOBID on $(hostname) at $(date -u +%FT%TZ) new=$NEW"
{ echo "jobid $JOBID"; md5sum $SHIPPED $INS/* $RUN/axes68/*; ls -l $ASIF $SIF; } > $LOG/provenance.log 2>&1

# ---------- shims: guard (t67) then attitude instrument (t67) ----------
$PY $INS/patch_guard67.py $SHIPPED $WORK/shim/G.cpp > $LOG/guard.log 2>&1 || { echo "!!!! guard patch failed"; exit 4; }
$PY $INS/patch_attitude67.py $WORK/shim/G.cpp $WORK/shim/GA.cpp > $LOG/attitude.log 2>&1 || { echo "!!!! attitude patch failed"; exit 4; }
md5sum $WORK/shim/G.cpp $WORK/shim/GA.cpp | tee -a $LOG/attitude.log

# ---------- include root: t58/t67 recipe ----------
$APT exec $ASIF cat /opt/sfs-pristine/class/data_path.h > $WORK/inc1/class/data_path.h 2>>$LOG/provenance.log
sed -i 's/^#define POT_A$/#define POT_A_INFRA_OFF_JUGLET/' $WORK/inc1/class/data_path.h
cp $T58/work/juglet_orig_block.inc $WORK/juglet_orig_block.inc
echo "BLOCK_MD5 $(md5sum $WORK/juglet_orig_block.inc | cut -d' ' -f1)  expect 401195eae5a41579563fc237a9843298" >> $LOG/provenance.log
cat $WORK/juglet_orig_block.inc >> $WORK/inc1/class/data_path.h

# stage one lane set into trees/<name>, then substitute axes68 (refuse unless exactly 9 Axes/ diffs)
stage_ax68 () {
  local NAME=$1 GEOM=$2
  mkdir -p $TREES/_$NAME
  $PY $INS/stage67_inputs.py --lanes $GEOM --dataset $DS --pota $POTA --out $TREES/_$NAME > $LOG/stage_$NAME.log 2>&1 \
    || { echo "!!!! staging $NAME failed"; return 5; }
  rm -rf $TREES/$NAME; mv $TREES/_$NAME/juglet $TREES/$NAME; rm -rf $TREES/_$NAME
  cp -r $TREES/$NAME $TREES/${NAME}_old
  cp -f $RUN/axes68/Juglet_Piece_?_Axis.xyz $TREES/$NAME/Axes/
  local N=$(diff -rq $TREES/${NAME}_old $TREES/$NAME | wc -l) NA=$(diff -rq $TREES/${NAME}_old $TREES/$NAME | grep -c '/Axes/')
  rm -rf $TREES/${NAME}_old
  echo "stage $NAME: diffs=$N axes=$NA" | tee -a $LOG/axes_subst.log
  [ "$N" -eq 9 ] && [ "$NA" -eq 9 ] || { echo "!!!! substitution not axes-only on $NAME"; return 5; }
  md5sum $TREES/$NAME/Breaklines/* >> $LOG/axes_subst.log
}

printf 'arm\tfloor\ttree\texit\twall_s\n' > $LOG/panel.tsv
runarm () {
  local ARM=$1 TREE=$2 T0=$SECONDS
  echo "##### LAUNCH $ARM tree=$TREE"
  $APT exec --writable-tmpfs --bind $MAIN:/workspace --bind $WORK:/panel --bind $OUT:/out --bind $TREE:/Dataset/SfS_pp \
     $ASIF bash /panel/arm67.sh $ARM 20 /panel/inc1 9 -DJUGLET_ORIG /panel/shim/GA.cpp >> $LOG/panel.log 2>&1
  local RC=$?
  printf '%s\t20\t%s\t%s\t%s\n' "$ARM" "$TREE" "$RC" "$((SECONDS - T0))" >> $LOG/panel.tsv
  echo "##### $ARM exit=$RC"
  $PY $T58/instruments/score58.py --result $OUT/$ARM --gt "$TREE/Ground Truth" --mesh "$TREE/Mesh" \
      --lanes "$TREE/Breaklines" --out $RUN/score/$ARM.json --label $ARM > $RUN/score/$ARM.stdout 2> $RUN/score/$ARM.stderr
  echo "score $ARM rc=$?"; cat "$OUT/$ARM/1. Acc.txt" 2>/dev/null
}

# ---------- 1) the per-pair instrument on F20N's inputs ----------
stage_ax68 t66 $LANES66 && runarm I20N $TREES/t66

# ---------- 2) edgeline binaries: stock and RESAMPLE_D_MM 0.95 from the same commit ----------
git -C $CANON fetch -q origin 68-axis-method-guard-densify >> $LOG/fetch.log 2>&1
git -C $CANON rev-parse --verify --quiet "$NEW^{commit}" > /dev/null || { echo "!!!! commit $NEW not in canon"; exit 2; }
ISRC=$RUN/instrsrc; rm -rf $ISRC; mkdir -p $ISRC
git -C $CANON archive $NEW .scratch/juglet-breaklines/stage55 .scratch/juglet-breaklines/stage66 | tar -x -C $ISRC
INSTR=$ISRC/.scratch/juglet-breaklines/stage66
STAGER=$ISRC/.scratch/juglet-breaklines/stage55/instruments/stage_synth_p40.sh
for V in s190 s095; do
  BT=$RUN/build_$V/src; rm -rf $RUN/build_$V; mkdir -p $BT/build
  git -C $CANON archive $NEW | tar -x -C $BT
  [ -d $BT/alglib ] || cp -a $CANON/alglib $BT/alglib
  if [ $V = s095 ]; then
    sed -i 's/const float RESAMPLE_D_MM = 1\.9f;/const float RESAMPLE_D_MM = 0.95f;/' $BT/edgeline_extraction_headless.cpp
    grep -q 'RESAMPLE_D_MM = 0.95f;' $BT/edgeline_extraction_headless.cpp || { echo "!!!! resample sed did not apply"; exit 4; }
  fi
  ( cd $BT/build && $APT exec --bind /data:/data $SIF cmake -DCMAKE_BUILD_TYPE=Release .. \
      && $APT exec --bind /data:/data $SIF make -j$P MeshPreprocessingHeadless EdgeLineExtractionHeadless ) > $LOG/build_$V.log 2>&1 \
    || { echo "!!!! build $V failed"; tail -30 $LOG/build_$V.log; exit 5; }
  cp -f $BT/build/MeshPreprocessingHeadless $RUN/bin-Mesh-$V
  cp -f $BT/build/EdgeLineExtractionHeadless $RUN/bin-Edge-$V
done
diff <(git -C $CANON show $NEW:edgeline_extraction_headless.cpp) $RUN/build_s095/src/edgeline_extraction_headless.cpp > $LOG/diff_resample.txt
md5sum $RUN/bin-* | tee $RUN/binaries.md5
cat $LOG/diff_resample.txt

# ---------- 3) cells: t66 recipe, Juglet arm U, stock vs 0.95 ----------
JUG="Juglet_Piece_1 Juglet_Piece_2 Juglet_Piece_3 Juglet_Piece_4 Juglet_Piece_5 Juglet_Piece_6 Juglet_Piece_7 Juglet_Piece_8 Juglet_Piece_9"
export CANON CORP DS SIF APT PY RUN RUNID NEW JOBID P INSTR STAGER
UNSET="-u SFS_NORMAL_SOURCE -u SFS_NORMAL_CARRY -u SFS_NORMAL_MIN_K -u SFS_NORMAL_MAX_K -u SFS_BREAK_STOP -u SFS_DEDUPE -u SFS_NORMAL_DUMP_DIR -u SFS_ADMIT_SIGN"
for V in s190 s095; do
  C=D${V#s}
  env $UNSET SFS_NORMAL_MODE=radius SFS_NORMAL_RADIUS_MM=1.0 MESH_BIN=$RUN/bin-Mesh-$V EDGE_BIN=$RUN/bin-Edge-$V \
      POT_NAME=Juglet PIECES="$JUG" WORNESS=0.7 MESH_ENV="" OUT=$RUN/out$C \
      CLOUD_DIR=$DS/Point/Juglet MESH_DIR=$DS/Mesh/Juglet AXIS_DIR=$DS/Axes/Juglet \
      MANIFEST=$DS/Point/Juglet/MANIFEST_JUGLET_CC.tsv MAN_MD5_COL=pcd_md5 MAN_PTS_COL=kept_points \
      bash $INSTR/run_cell66.sh > $LOG/cell_$C.log 2>&1
  echo "cell $C rc=$?"; tail -12 $LOG/cell_$C.log
  md5sum $RUN/out$C/geom/* > $RUN/out$C.geom.md5 2>/dev/null
done

# ---------- 4) instrumented F20 panel on the new lanes, axes68 ----------
for C in D190 D095; do
  stage_ax68 t$C $RUN/out$C/geom && runarm I20_$C $TREES/t$C
done

md5sum $WORK/shim/*.cpp $WORK/build/Hierarchy-* 2>/dev/null > $LOG/md5_binaries.txt
cp $WORK/logs/* $LOG/ 2>/dev/null
cat $LOG/panel.tsv
for A in I20N I20_D190 I20_D095; do echo "[$A]"; grep -E "Total number|Node Sequence|T67-" $WORK/logs/binary_$A.log | head -5; wc -l $OUT/$A/T67_*.tsv 2>/dev/null; done
echo "=== t68c job finished $(date -u +%FT%TZ)"
