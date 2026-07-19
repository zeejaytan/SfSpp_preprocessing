#!/bin/bash
#SBATCH --job-name=mesh_adapt
#SBATCH --output=mesh_adaptive.log
#SBATCH --error=mesh_adaptive.err
#SBATCH --time=02:00:00
#SBATCH --mem=32G
#SBATCH --cpus-per-task=4
#SBATCH --partition=sapphire

module load Apptainer

CONTAINER="/data/gpfs/projects/punim2657/sfs_preprocessing/pcl_191_nurbs.sif"
BIND="/data/gpfs/projects/punim2657:/data/gpfs/projects/punim2657"
WORK_DIR="/data/gpfs/projects/punim2657/sfs_preprocessing"

cd $WORK_DIR

echo "========== Testing with conservative adaptive parameters =========="
echo "Binary timestamp: $(ls -lh build_new/MeshPreprocessingHeadless)"
echo ""

# Run without arguments to process all pieces
apptainer exec --bind $BIND $CONTAINER \
    ./build_new/MeshPreprocessingHeadless

echo ""
echo "========== Results for all pieces =========="
for i in 01 02 03 04 05 06 07 08; do
    echo "Piece $i:"
    echo -n "  S0: "; wc -l < Temp/Data/Pot_A/Pot_A_Piece_${i}_Surface_0.xyz 2>/dev/null || echo "N/A"
    echo -n "  S1: "; wc -l < Temp/Data/Pot_A/Pot_A_Piece_${i}_Surface_1.xyz 2>/dev/null || echo "N/A"
done

echo ""
echo "========== Sample comparison =========="
for i in 01 02 03 04 05 06 07 08; do
    echo "Piece $i Sample:"
    echo -n "  S0: "; wc -l < /data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp/Surfaces/Pot_A_Piece_${i}_Surface_0.xyz 2>/dev/null || echo "N/A"
    echo -n "  S1: "; wc -l < /data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp/Surfaces/Pot_A_Piece_${i}_Surface_1.xyz 2>/dev/null || echo "N/A"
done
