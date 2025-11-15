#!/bin/bash
#SBATCH --job-name=nurbs_edgeline_proper_curvature
#SBATCH --time=00:45:00
#SBATCH --mem=8G
#SBATCH --cpus-per-task=2
#SBATCH --partition=sapphire
#SBATCH --output=nurbs_edgeline_proper_curvature_%j.out
#SBATCH --error=nurbs_edgeline_proper_curvature_%j.err

echo "=== NURBS EdgeLine Extraction with Proper Geometric Curvature ==="
echo "Job ID: $SLURM_JOB_ID"
echo "Start time: $(date)"
echo "Using EdgeLineExtractionHeadless with NURBS surface derivative computation"
echo

cd /data/gpfs/projects/punim2657/sfs_preprocessing/original_nurbs_preprocessing

# Create necessary directories
mkdir -p Temp/Axes Temp/Data/Pot_A Breaklines

echo "Running NURBS EdgeLine extraction with proper curvature computation..."
CONTAINER_PATH="/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer"
$CONTAINER_PATH exec \
    --bind /data/gpfs/projects/punim2657/sfs_preprocessing/original_nurbs_preprocessing:/workspace \
    --pwd /workspace \
    /data/gpfs/projects/punim2657/sfs_preprocessing/pcl_191_nurbs.sif \
    ./build/EdgeLineExtractionHeadless A 8

echo
echo "EdgeLine extraction completed at: $(date)"

# Check for generated files
echo "=== Generated NURBS Breakline Files with Proper Curvature ==="
find . -name "*Breakline*.pcd" -exec echo "NURBS Breakline: {}" \;
find . -name "*Surface_F*" -exec echo "NURBS Surface_F: {}" \;

# Show sample curvature values to verify proper computation
echo
echo "=== Verifying Proper Curvature Values (should show geometric values, not 2e+26) ==="
if [ -f "Pot_A_Piece_01_Breakline_0.pcd" ]; then
    echo "Sample curvature values from Pot_A_Piece_01_Breakline_0.pcd:"
    tail -5 Pot_A_Piece_01_Breakline_0.pcd | awk '{print "  Point: " $1 " " $2 " " $3 " | Normal: " $4 " " $5 " " $6 " | Curvature: " $7}'
fi

# Copy to organized dataset structure
echo
echo "=== Organizing Results into Dataset Structure ==="
DATASET_DIR="NURBS_Dataset_$(date +%Y%m%d)_ProperCurvature"
mkdir -p "../$DATASET_DIR/SfS_pp/Breaklines"
mkdir -p "../$DATASET_DIR/SfS_pp/Surfaces"

# Copy generated files to organized structure
if ls *Breakline*.pcd 1> /dev/null 2>&1; then
    cp *Breakline*.pcd "../$DATASET_DIR/SfS_pp/Breaklines/"
    echo "Breaklines copied to $DATASET_DIR/SfS_pp/Breaklines/"
fi

if ls *Surface_F*.xyz 1> /dev/null 2>&1; then
    cp *Surface_F*.xyz "../$DATASET_DIR/SfS_pp/Surfaces/" 
    echo "Surface_F files copied to $DATASET_DIR/SfS_pp/Surfaces/"
fi

# Copy original surfaces
cp Dataset/SfS_pp/Surfaces/*.xyz "../$DATASET_DIR/SfS_pp/Surfaces/"
echo "Original NURBS surfaces copied to dataset"

echo
echo "=== Running Axis Extraction ==="
echo "Extracting pottery axes using existing SLURM parallel approach..."

# Create axes output directory
mkdir -p "../$DATASET_DIR/SfS_pp/Axes"

# Use NURBS-specific axis extraction system 
echo "Running NURBS axis extraction using PotSAC algorithm..."
module load MATLAB/2024b_Update_3

# Run NURBS axis extraction from the NURBS preprocessing directory
cd /data/gpfs/projects/punim2657/sfs_preprocessing/original_nurbs_preprocessing

# Check that NURBS surfaces are available for axis extraction
echo "Verifying NURBS surfaces are available:"
ls -la Dataset/SfS_pp/Surfaces/Pot_A_Piece_*_Surface_*.xyz | head -5

# Execute NURBS axis extraction
echo "Executing NURBS PotSAC axis extraction..."
matlab -batch "extract_all_nurbs_axes"

# Copy results to the new dataset structure
if [ -d "NURBS_Output/Axes" ]; then
    cp NURBS_Output/Axes/*.xyz "/data/gpfs/projects/punim2657/sfs_preprocessing/$DATASET_DIR/SfS_pp/Axes/"
    echo "✓ NURBS axis extraction completed - copied $(ls NURBS_Output/Axes/*.xyz 2>/dev/null | wc -l) axis files"
    echo "Generated axes using NURBS B-spline surface fitting (not TPS)"
elif [ -d "Dataset/SfS_pp/Axes" ]; then
    # Fallback: copy axes from existing NURBS dataset
    cp Dataset/SfS_pp/Axes/*.xyz "/data/gpfs/projects/punim2657/sfs_preprocessing/$DATASET_DIR/SfS_pp/Axes/"
    echo "⚠ Fallback: Copied existing NURBS axes ($(ls Dataset/SfS_pp/Axes/*.xyz 2>/dev/null | wc -l) files)"
else
    echo "❌ NURBS axis extraction failed - no axes generated"
fi

echo "=== Dataset Organization Complete ==="
echo "Complete NURBS dataset with proper curvature available at: /data/gpfs/projects/punim2657/sfs_preprocessing/$DATASET_DIR"
echo "Dataset includes:"
echo "  - Surfaces: $(ls ../\"$DATASET_DIR\"/SfS_pp/Surfaces/*.xyz | wc -l) files"
echo "  - Breaklines: $(ls ../\"$DATASET_DIR\"/SfS_pp/Breaklines/*.pcd | wc -l) files"  
echo "  - Axes: $(ls ../\"$DATASET_DIR\"/SfS_pp/Axes/*.xyz 2>/dev/null | wc -l) files"

echo "=== Job Finished ==="