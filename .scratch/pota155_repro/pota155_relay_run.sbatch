#!/bin/bash
#SBATCH --job-name=p155_relay
#SBATCH --output=p155_relay.log
#SBATCH --error=p155_relay.err
#SBATCH --time=02:00:00
#SBATCH --mem=16G
#SBATCH --cpus-per-task=4
#SBATCH --partition=sapphire

module load Apptainer
SIF=/data/gpfs/projects/punim2657/sfs_preprocessing/pcl_191_nurbs.sif
TREE=/data/gpfs/projects/punim2657/sfs_cure_1c6a8f9
SUB=$TREE/original_nurbs_preprocessing
APT=/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer
cd $TREE

echo "===== BASELINE: stash cure, rebuild, run Pot_A P01 ====="
git stash push $SUB/edgeline_extraction_headless.cpp $SUB/edge_line_ordering.cpp
$APT exec --bind /data:/data $SIF /bin/bash -c "cd $SUB/build && make EdgeLineExtractionHeadless -j4 > make_base.log 2>&1; echo BASE-BUILD-EXIT:$?"
cp $SUB/build/EdgeLineExtractionHeadless $TREE/EdgeLine_BASE
mkdir -p $TREE/Temp_base
$APT exec --bind /data:/data $SIF env POT_NAME=Pot_A $SUB/build/EdgeLineExtractionHeadless --potID Pot_A --pieceNo Piece_01 --datasetPath $TREE/Dataset --tempPath $TREE/Temp_base > $TREE/run_base.log 2>&1
echo "BASE-RUN-EXIT:$?"
mkdir -p $TREE/Breaklines_base && cp $TREE/Dataset/Breaklines/Pot_A/Pot_A_Piece_01_Breakline_*.pcd $TREE/Breaklines_base/

echo "===== CURED: unstash, rebuild, run Pot_A P01 ====="
git stash pop
$APT exec --bind /data:/data $SIF /bin/bash -c "cd $SUB/build && make EdgeLineExtractionHeadless -j4 > make_cure.log 2>&1; echo CURE-BUILD-EXIT:$?"
mkdir -p $TREE/Temp_cure
$APT exec --bind /data:/data $SIF env POT_NAME=Pot_A $SUB/build/EdgeLineExtractionHeadless --potID Pot_A --pieceNo Piece_01 --datasetPath $TREE/Dataset --tempPath $TREE/Temp_cure > $TREE/run_cure.log 2>&1
echo "CURE-RUN-EXIT:$?"
mkdir -p $TREE/Breaklines_cure && cp $TREE/Dataset/Breaklines/Pot_A/Pot_A_Piece_01_Breakline_*.pcd $TREE/Breaklines_cure/

echo "===== EVIDENCE ====="
grep -h 'FACE VETO' $TREE/run_cure.log | head -5
grep -h 'SPLIT-WALK' $TREE/run_cure.log | head -5
echo "--- breakline counts (base vs cure):"
wc -l $TREE/Breaklines_base/*.pcd $TREE/Breaklines_cure/*.pcd
echo "===== DONE ====="
