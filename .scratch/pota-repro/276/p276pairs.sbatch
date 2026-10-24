#!/bin/bash
#SBATCH --job-name=p276pairs
#SBATCH --time=02:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G
#SBATCH --output=/data/gpfs/projects/punim2657/SfSpp/runs/20261024-1121_0ab0935_p276-merge/logs/p276pairs_%j.out
set -u
APT=/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer
SIF=/data/gpfs/projects/punim2657/sfs_preprocessing/pcl_191_nurbs.sif
WT=/data/gpfs/projects/punim2657/sfs_preprocessing.wt/276
MESHB=$WT/build/MeshPreprocessingHeadless
R=/data/gpfs/projects/punim2657/SfSpp/runs/20261024-1121_0ab0935_p276-merge
echo MESH_MD5=$(md5sum $MESHB | cut -d' ' -f1)
run_split () {
  TAG=$1; POT=$2; NN=$3; SRC=$4; RANK=$5; EXTRA=$6
  STAGE=$R/stage/$TAG; OUTD=$R/out3/$TAG
  rm -rf $STAGE $OUTD
  mkdir -p $STAGE/Dataset/Point/$POT $STAGE/Dataset/Mesh/$POT $STAGE/Dataset/Axes $STAGE/Dataset/Breaklines/$POT $STAGE/Dataset/Surfaces/$POT $STAGE/Temp $OUTD
  cp $SRC/Point/$POT/${POT}_Piece_${NN}_Point.pcd $STAGE/Dataset/Point/$POT/
  cp $SRC/Mesh/$POT/${POT}_Piece_${NN}_Mesh.obj $STAGE/Dataset/Mesh/$POT/
  cp $SRC/Axes/${POT}_Piece_${NN}_Axis.xyz $STAGE/Dataset/Axes/
  md5sum $STAGE/Dataset/Point/$POT/*.pcd $STAGE/Dataset/Mesh/$POT/*.obj $STAGE/Dataset/Axes/*.xyz > $OUTD/inputs.md5
  cd $STAGE || return 1
  T0=$(date +%s)
  $APT exec --bind /data:/data $SIF env POT_NAME=$POT SFS_PAPER_THETA=4.0 SFS_AXIS_FILE=$STAGE/Dataset/Axes/${POT}_Piece_${NN}_Axis.xyz SFS_MERGE_DIAG=split SFS_MERGE_SPLIT_RANK=$RANK $EXTRA $MESHB > $OUTD/mesh.log 2>&1
  echo "TAG=$TAG RANK=$RANK EXTRA=$EXTRA EXIT=$? SECS=$(( $(date +%s) - T0 ))" | tee $OUTD/exit.txt
  grep -m1 'classify:' $OUTD/mesh.log
  grep -c 'PAIR-276' $OUTD/mesh.log | sed 's/^/PAIRLINES=/'
  grep -E 'PAIR-276.*verdict=' $OUTD/mesh.log | grep -E 'c[0-9]+-c[0-9]+ ' | head -40
  grep -E 'pass [0-9]+ (done|:)' $OUTD/mesh.log
  mv mergeDiag276_*.txt $OUTD/ 2>/dev/null || echo NO_DIAG_DUMP
  echo "--- end $TAG"
}
run_split C03_split_r0 Pot_C 03 $R/inputs/C03_diag 0 SFS_MERGE_PAIRS=1
run_split C03_split_r2 Pot_C 03 $R/inputs/C03_diag 2 SFS_MERGE_PAIRS=1
run_split H02_split_r0 Pot_H 02 $R/inputs/H02_diag 0 SFS_MERGE_PAIRS=1
run_split C01_split Pot_C 01 $R/inputs/C01_diag 0 SFS_MERGE_PAIRS=1
run_split C03_split_r0_nopairs Pot_C 03 $R/inputs/C03_diag 0 SFS_AXIS_FILE_SET=1
echo ALL_DONE
