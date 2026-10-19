#!/bin/bash
#SBATCH --job-name=p155_v5
#SBATCH --output=p155_v5.log
#SBATCH --error=p155_v5.err
#SBATCH --time=02:00:00
#SBATCH --mem=16G
#SBATCH --cpus-per-task=4
#SBATCH --partition=sapphire

module load Apptainer
SIF=/data/gpfs/projects/punim2657/sfs_preprocessing/pcl_191_nurbs.sif
SUB=/data/gpfs/projects/punim2657/sfs_cure_1c6a8f9/original_nurbs_preprocessing
TREE=/data/gpfs/projects/punim2657/sfs_cure_1c6a8f9
APT=/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer
PRODBIN=/data/gpfs/projects/punim2657/sfs_preprocessing/original_nurbs_preprocessing/build/EdgeLineExtractionHeadless

echo "===== MESH STAGE (CWD=subcopy) ====="
$APT exec --bind /data:/data $SIF bash -c "cd $SUB && ./build/MeshPreprocessingHeadless > $TREE/meshrun5.log 2>&1; echo MESH-RUN-EXIT:$?"
ls $SUB/Temp/Data/Pot_A/*.xyz 2>/dev/null || echo "NO SURFACES"

echo "===== BASELINE (production Oct16 binary, CWD=subcopy) ====="
$APT exec --bind /data:/data $SIF bash -c "cd $SUB && $PRODBIN > $TREE/run_base5.log 2>&1; echo BASE-RUN-EXIT:$?"
mkdir -p $TREE/Breaklines_base && cp $SUB/build/Pot_A_Piece_01_Breakline_*.pcd $TREE/Breaklines_base/

echo "===== CURED (worktree binary, same CWD) ====="
$APT exec --bind /data:/data $SIF bash -c "cd $SUB && ./build/EdgeLineExtractionHeadless > $TREE/run_cure5.log 2>&1; echo CURE-RUN-EXIT:$?"
mkdir -p $TREE/Breaklines_cure && cp $SUB/build/Pot_A_Piece_01_Breakline_*.pcd $TREE/Breaklines_cure/

echo "===== EVIDENCE ====="
grep -h 'FACE VETO' $TREE/run_cure5.log | head -5
grep -h 'SPLIT-WALK' $TREE/run_cure5.log | head -5
echo "--- breakline counts (base vs cure):"
wc -l $TREE/Breaklines_base/*.pcd $TREE/Breaklines_cure/*.pcd 2>/dev/null
echo "===== DONE ====="
