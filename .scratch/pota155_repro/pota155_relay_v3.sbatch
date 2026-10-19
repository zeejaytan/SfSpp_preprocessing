#!/bin/bash
#SBATCH --job-name=p155_v3
#SBATCH --output=p155_v3.log
#SBATCH --error=p155_v3.err
#SBATCH --time=02:00:00
#SBATCH --mem=16G
#SBATCH --cpus-per-task=4
#SBATCH --partition=sapphire

module load Apptainer
module load CloudCompare/2.12.4
SIF=/data/gpfs/projects/punim2657/sfs_preprocessing/pcl_191_nurbs.sif
TREE=/data/gpfs/projects/punim2657/sfs_cure_1c6a8f9
SUB=$TREE/original_nurbs_preprocessing
APT=/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer
PRODBIN=/data/gpfs/projects/punim2657/sfs_preprocessing/original_nurbs_preprocessing/build/EdgeLineExtractionHeadless
cd $TREE

echo "===== STAGE: sample mesh + mesh surfaces (piece 01 only) ====="
rm -rf $SUB/Temp && mkdir -p $SUB/Temp/Data/Pot_A
CloudCompare -SILENT -O $TREE/Dataset/Mesh/Pot_A/Pot_A_Piece_01_Mesh.obj -SAMPLE_MESH POINTS 50000 -COMPUTE_NORMALS -C_EXPORT_FMT PCD -SAVE_CLOUDS FILE $SUB/build/Pot_A_Piece_01_Point.pcd
cp $SUB/build/Pot_A_Piece_01_Point.pcd $SUB/Temp/Data/Pot_A/
$APT exec --bind /data:/data $SIF bash -c "cd $SUB/build && cmake .. > /dev/null 2>&1 && make MeshPreprocessingHeadless -j4 > meshbuild.log 2>&1; echo MESH-BUILD-EXIT:$?"
$APT exec --bind /data:/data $SIF bash -c "cd $SUB/build && ./MeshPreprocessingHeadless > meshrun.log 2>&1; echo MESH-RUN-EXIT:$?"
ls $SUB/Temp/Data/Pot_A/*.xyz 2>/dev/null || echo "NO SURFACES"

echo "===== BASELINE: production Oct16 binary on staged inputs ====="
$APT exec --bind /data:/data $SIF bash -c "cd $SUB/build && $PRODBIN > $TREE/run_base3.log 2>&1; echo BASE-RUN-EXIT:$?"
mkdir -p $TREE/Breaklines_base && cp $SUB/build/Pot_A_Piece_01_Breakline_*.pcd $TREE/Breaklines_base/

echo "===== CURED: worktree binary on same inputs ====="
$APT exec --bind /data:/data $SIF bash -c "cd $SUB/build && ./EdgeLineExtractionHeadless > $TREE/run_cure3.log 2>&1; echo CURE-RUN-EXIT:$?"
mkdir -p $TREE/Breaklines_cure && cp $SUB/build/Pot_A_Piece_01_Breakline_*.pcd $TREE/Breaklines_cure/

echo "===== EVIDENCE ====="
grep -h 'FACE VETO' $TREE/run_cure3.log | head -5
grep -h 'SPLIT-WALK' $TREE/run_cure3.log | head -5
echo "--- breakline counts (base vs cure):"
wc -l $TREE/Breaklines_base/*.pcd $TREE/Breaklines_cure/*.pcd
echo "===== DONE ====="
