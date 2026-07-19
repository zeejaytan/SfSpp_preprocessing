#!/bin/bash
#SBATCH --job-name=coord_fix_test
#SBATCH --time=02:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --output=coord_fix_test_%j.log
#SBATCH --error=coord_fix_test_%j.err

cd /data/gpfs/projects/punim2657/sfs_preprocessing

echo "========================================"
echo "Testing Coordinate Fix - All 8 Pieces"
echo "Build time: $(ls -lh build_new/EdgeLineExtractionHeadless | awk '{print $6, $7, $8}')"
echo "========================================"
echo ""

module load Apptainer/1.3.3

CONTAINER="pcl_191_nurbs.sif"
WORKDIR="/data/gpfs/projects/punim2657/sfs_preprocessing"
EXECUTABLE="./build_new/EdgeLineExtractionHeadless"

# Process all 8 pieces
for i in 01 02 03 04 05 06 07 08; do
    echo ""
    echo "===================="
    echo "Processing Piece_${i}"
    echo "===================="

    timeout 300 apptainer exec --bind /data:/data ${CONTAINER} \
        ${EXECUTABLE} \
        ${WORKDIR}/Dataset/Surfaces/Pot_A/Pot_A_Piece_${i}_Surface 2 Pot_A Piece_${i}

    if [ $? -eq 0 ]; then
        echo "[SUCCESS] Piece_${i} completed"

        # Check coordinate scale
        echo ""
        echo "Checking BL0 coordinates:"
        coord0=$(grep "^[0-9\-]" Dataset/Breaklines/Pot_A/Pot_A_Piece_${i}_Breakline_0.pcd 2>/dev/null | head -1)
        echo "  First point: ${coord0}" | awk '{printf "  (%.2f, %.2f, %.2f)\n", $3, $4, $5}'

        echo "Checking BL1 coordinates:"
        coord1=$(grep "^[0-9\-]" Dataset/Breaklines/Pot_A/Pot_A_Piece_${i}_Breakline_1.pcd 2>/dev/null | head -1)
        echo "  First point: ${coord1}" | awk '{printf "  (%.2f, %.2f, %.2f)\n", $3, $4, $5}'

        echo ""
    else
        echo "[ERROR] Piece_${i} failed with exit code $?"
    fi
done

echo ""
echo "========================================"
echo "Coordinate Fix Verification"
echo "========================================"
echo ""
echo "Summary of BL0 first point coordinates:"
echo "(Should be in mm scale: X≈-22 to +64, Y≈-33 to +42, Z≈376-411)"
echo ""

for i in 01 02 03 04 05 06 07 08; do
    printf "Piece_%s BL0: " "${i}"
    grep "^[0-9\-]" Dataset/Breaklines/Pot_A/Pot_A_Piece_${i}_Breakline_0.pcd 2>/dev/null | head -1 | awk '{printf "X=%.1f, Y=%.1f, Z=%.1f\n", $1, $2, $3}'
done

echo ""
echo "If coordinates are ~50,000-400,000 range, bug still present (micrometers)"
echo "If coordinates are ~-30 to +70 range for X/Y, ~300-450 for Z, bug is fixed (millimeters)"
