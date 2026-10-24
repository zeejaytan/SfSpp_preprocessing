#!/bin/bash
#SBATCH --job-name=p276_0b
#SBATCH --time=04:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G
#SBATCH --output=/data/gpfs/projects/punim2657/SfSpp/runs/20261024-1121_0ab0935_p276-merge/logs/p276_0b_%j.out
set -u
APT=/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer
SIF=/data/gpfs/projects/punim2657/sfs_preprocessing/pcl_191_nurbs.sif
WT=/data/gpfs/projects/punim2657/sfs_preprocessing.wt/276
MESHB=$WT/build/MeshPreprocessingHeadless
R=/data/gpfs/projects/punim2657/SfSpp/runs/20261024-1121_0ab0935_p276-merge
echo "MESH_MD5=$(md5sum $MESHB | cut -d' ' -f1)"
echo "MESH_DIAG_STRINGS=$(strings $MESHB | grep -c 'MERGE-DIAG-276')"
run_mesh () {
  TAG=$1; POT=$2; NN=$3; TREED=$4; DIAG=$5
  TREE=/data/gpfs/projects/punim2657/$TREED
  STAGE=$R/stage/$TAG
  OUTD=$R/out/$TAG
  rm -rf $STAGE $OUTD
  mkdir -p $STAGE/Dataset/Point/$POT $STAGE/Dataset/Mesh/$POT $STAGE/Dataset/Axes $STAGE/Dataset/Breaklines/$POT $STAGE/Dataset/Surfaces/$POT $STAGE/Temp $OUTD
  cp $TREE/Dataset/Point/$POT/${POT}_Piece_${NN}_Point.pcd $STAGE/Dataset/Point/$POT/
  cp $TREE/Dataset/Mesh/$POT/${POT}_Piece_${NN}_Mesh.obj $STAGE/Dataset/Mesh/$POT/
  cp $TREE/Dataset/Axes/${POT}_Piece_${NN}_Axis.xyz $STAGE/Dataset/Axes/
  md5sum $STAGE/Dataset/Point/$POT/*.pcd $STAGE/Dataset/Mesh/$POT/*.obj $STAGE/Dataset/Axes/*.xyz > $OUTD/inputs.md5
  ( cd $TREE && md5sum Dataset/Surfaces/$POT/${POT}_Piece_${NN}_Surface_0.xyz Dataset/Surfaces/$POT/${POT}_Piece_${NN}_Surface_1.xyz Temp/Data/$POT/${POT}_Piece_${NN}_Surface_0.xyz Temp/Data/$POT/${POT}_Piece_${NN}_Surface_1.xyz 2>/dev/null ) > $OUTD/tree_sheets.md5
  ( cd /data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp/Breaklines && md5sum ${POT}_Piece_${NN}_Breakline_0.pcd ${POT}_Piece_${NN}_Breakline_1.pcd ) > $OUTD/author.md5
  ( cd $TREE && md5sum Dataset/Breaklines/$POT/${POT}_Piece_${NN}_Breakline_0.pcd Dataset/Breaklines/$POT/${POT}_Piece_${NN}_Breakline_1.pcd 2>/dev/null ) > $OUTD/tree_breaklines.md5
  cd $STAGE || return 1
  T0=$(date +%s)
  $APT exec --bind /data:/data $SIF env POT_NAME=$POT SFS_PAPER_THETA=4.0 SFS_AXIS_FILE=$STAGE/Dataset/Axes/${POT}_Piece_${NN}_Axis.xyz ${DIAG:+SFS_MERGE_DIAG=$DIAG} $MESHB > $OUTD/mesh.log 2>&1
  EX=$?
  echo "TAG=$TAG POT=$POT NN=$NN DIAG='$DIAG' EXIT=$EX SECS=$(( $(date +%s) - T0 ))" | tee $OUTD/exit.txt
  grep -m1 'paper grow' $OUTD/mesh.log
  grep -m1 'Number of clusters' $OUTD/mesh.log
  grep -m1 'Points in two clusters' $OUTD/mesh.log
  grep -m1 'classify:' $OUTD/mesh.log
  grep 'appendix-A merge' $OUTD/mesh.log
  grep 'MERGE-DIAG-276' $OUTD/mesh.log
  mv mergeDiag276_*.txt $OUTD/ 2>/dev/null || echo "TAG=$TAG NO_DIAG_DUMP"
  md5sum Temp/Data/$POT/${POT}_Piece_${NN}_Surface_0.xyz Temp/Data/$POT/${POT}_Piece_${NN}_Surface_1.xyz > $OUTD/sheets.md5 2>/dev/null
  wc -l Temp/Data/$POT/${POT}_Piece_${NN}_Surface_0.xyz Temp/Data/$POT/${POT}_Piece_${NN}_Surface_1.xyz >> $OUTD/sheets.md5 2>/dev/null
  cp -f $OUTD/mesh.log $OUTD/ 2>/dev/null || true
  echo "--- end $TAG"
}
run_mesh H02_diag Pot_H 02 pota257_paper_Pot_H_02 1
run_mesh H10_diag Pot_H 10 pota257_paper_Pot_H_10 1
run_mesh C03_diag Pot_C 03 pota251_paper_Pot_C_03 1
run_mesh C01_diag Pot_C 01 pota251_paper_Pot_C_01 1
run_mesh C01_nodiag Pot_C 01 pota251_paper_Pot_C_01 ''
run_mesh B01_diag Pot_B 01 pota253_paper_Pot_B_01 1
echo ALL_DONE
