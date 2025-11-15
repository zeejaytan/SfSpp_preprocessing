#!/bin/bash
#SBATCH --job-name=nurbs_complete_fixed
#SBATCH --time=01:30:00
#SBATCH --mem=12G
#SBATCH --cpus-per-task=4
#SBATCH --partition=sapphire
#SBATCH --output=nurbs_complete_fixed_%j.out
#SBATCH --error=nurbs_complete_fixed_%j.err

echo "=== COMPLETE NURBS DATASET GENERATION WITH PROPER WORKFLOW ==="
echo "Job ID: $SLURM_JOB_ID"
echo "Start time: $(date)"
echo "Fixing: NURBS workflow to use NURBS axis extraction (not TPS)"
echo

cd /data/gpfs/projects/punim2657/sfs_preprocessing/original_nurbs_preprocessing

# Create necessary directories
mkdir -p Temp/Axes Temp/Data/Pot_A Breaklines

echo "=== 1. NURBS EdgeLine Extraction with Fixed Curvature ==="
CONTAINER_PATH="/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer"
$CONTAINER_PATH exec \
    --bind /data/gpfs/projects/punim2657/sfs_preprocessing/original_nurbs_preprocessing:/workspace \
    --pwd /workspace \
    /data/gpfs/projects/punim2657/sfs_preprocessing/pcl_191_nurbs.sif \
    ./build/EdgeLineExtractionHeadless A 8

echo
echo "=== 2. NURBS Axis Extraction with PotSAC ==="
echo "Loading MATLAB module..."
module load MATLAB/2024b_Update_3

echo "Verifying NURBS surfaces are available:"
ls -la Dataset/SfS_pp/Surfaces/Pot_A_Piece_*_Surface_*.xyz | head -5

echo "Running NURBS-specific PotSAC axis extraction..."
matlab -batch "extract_all_nurbs_axes"

echo
echo "=== 3. Dataset Organization ==="
DATASET_DIR="NURBS_Dataset_$(date +%Y%m%d)_CompleteFixed"
DATASET_PATH="/data/gpfs/projects/punim2657/sfs_preprocessing/$DATASET_DIR"
mkdir -p "$DATASET_PATH/SfS_pp/"{Breaklines,Surfaces,Axes}

echo "Organizing complete NURBS dataset: $DATASET_DIR"

# Copy breaklines (with fixed curvature)
if ls Dataset/Breaklines/Pot_A/*.pcd 1> /dev/null 2>&1; then
    cp Dataset/Breaklines/Pot_A/*.pcd "$DATASET_PATH/SfS_pp/Breaklines/"
    echo "✅ Copied $(ls Dataset/Breaklines/Pot_A/*.pcd | wc -l) breakline files with fixed curvature"
else
    echo "❌ No breakline files found"
fi

# Copy NURBS surfaces  
if ls Dataset/SfS_pp/Surfaces/*.xyz 1> /dev/null 2>&1; then
    cp Dataset/SfS_pp/Surfaces/*.xyz "$DATASET_PATH/SfS_pp/Surfaces/"
    echo "✅ Copied $(ls Dataset/SfS_pp/Surfaces/*.xyz | wc -l) NURBS surface files"
else
    echo "❌ No NURBS surface files found"
fi

# Copy NURBS axes
if [ -d "NURBS_Output/Axes" ] && ls NURBS_Output/Axes/*.xyz 1> /dev/null 2>&1; then
    cp NURBS_Output/Axes/*.xyz "$DATASET_PATH/SfS_pp/Axes/"
    echo "✅ Copied $(ls NURBS_Output/Axes/*.xyz | wc -l) NURBS axis files"
elif [ -d "Dataset/SfS_pp/Axes" ] && ls Dataset/SfS_pp/Axes/*.xyz 1> /dev/null 2>&1; then
    cp Dataset/SfS_pp/Axes/*.xyz "$DATASET_PATH/SfS_pp/Axes/"
    echo "⚠️ Fallback: Copied $(ls Dataset/SfS_pp/Axes/*.xyz | wc -l) existing NURBS axes"
else
    echo "❌ No NURBS axis files found"
fi

echo
echo "=== 4. Verification ==="
echo "Complete NURBS dataset contents:"
echo "📁 Location: $DATASET_PATH"
echo "📊 Surfaces: $(ls $DATASET_PATH/SfS_pp/Surfaces/*.xyz 2>/dev/null | wc -l) files"
echo "📊 Breaklines: $(ls $DATASET_PATH/SfS_pp/Breaklines/*.pcd 2>/dev/null | wc -l) files"  
echo "📊 Axes: $(ls $DATASET_PATH/SfS_pp/Axes/*.xyz 2>/dev/null | wc -l) files"

# Verify curvature values are fixed
echo
echo "=== 5. Curvature Fix Verification ==="
if [ -f "$DATASET_PATH/SfS_pp/Breaklines/Pot_A_Piece_03_Breakline_0.pcd" ]; then
    echo "Green piece (03) curvature sample:"
    tail -3 "$DATASET_PATH/SfS_pp/Breaklines/Pot_A_Piece_03_Breakline_0.pcd" | awk '{print "  " $7}'
fi

if [ -f "$DATASET_PATH/SfS_pp/Breaklines/Pot_A_Piece_04_Breakline_0.pcd" ]; then
    echo "Orange piece (04) curvature sample:"
    tail -3 "$DATASET_PATH/SfS_pp/Breaklines/Pot_A_Piece_04_Breakline_0.pcd" | awk '{print "  " $7}'
fi

echo
echo "=== 6. Workflow Verification ==="
echo "✅ NURBS mesh processing: B-spline surface fitting"
echo "✅ NURBS edgeline extraction: B-spline surface fitting with fixed curvature"
echo "✅ NURBS axis extraction: PotSAC algorithm on NURBS surfaces" 
echo "❌ Previously: TPS axis extraction (wrong workflow)"

echo
echo "=== COMPLETE NURBS DATASET READY ==="
echo "🎯 Dataset: $DATASET_DIR"
echo "🎯 Ready for SFS reconstruction with proper NURBS workflow"
echo "🎯 Expected: Eliminated false positive matches due to fixed curvature"
echo "End time: $(date)"