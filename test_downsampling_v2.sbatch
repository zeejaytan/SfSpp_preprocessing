#!/bin/bash
#SBATCH --job-name=test_downsampling_13k
#SBATCH --time=00:30:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G

cd /data/gpfs/projects/punim2657/sfs_preprocessing

# Load modules
module load GCCcore/11.3.0
module load CMake
module load Apptainer

echo "=== TEST 1: Downsampling to 13,000 points (0.20mm estimate) ==="
echo "Started: $(date)"

# Clean previous output
rm -rf Dataset/Surfaces/Pot_A/*
rm -rf build && mkdir build && cd build

# Build in container with cmake - only MeshPreprocessingHeadless
echo "Building MeshPreprocessingHeadless..."
apptainer exec --bind /data:/data /data/gpfs/projects/punim2657/sfs_preprocessing/pcl_191_nurbs.sif bash << 'INNER'
cd /data/gpfs/projects/punim2657/sfs_preprocessing/build
cmake .. -DCMAKE_BUILD_TYPE=Release
make MeshPreprocessingHeadless -j4
INNER

# Check if build succeeded
if [ -f /data/gpfs/projects/punim2657/sfs_preprocessing/build/MeshPreprocessingHeadless ]; then
    echo "Build successful!"
else
    echo "Build failed!"
    exit 1
fi

# Run mesh preprocessing
echo ""
echo "Running MeshPreprocessingHeadless..."
cd /data/gpfs/projects/punim2657/sfs_preprocessing
apptainer exec --bind /data:/data /data/gpfs/projects/punim2657/sfs_preprocessing/pcl_191_nurbs.sif ./build/MeshPreprocessingHeadless 2>&1 | grep -E "DOWNSAMPLING RESULT|Starting|error" | tail -20

# Check result point counts
echo ""
echo "=== POINT COUNT RESULTS (TEST 1: target 13K) ==="
count=0
for f in Dataset/Surfaces/Pot_A/Pot_A_Piece_*_Surface_*.xyz; do
    if [ -f "$f" ]; then
        pts=$(wc -l < "$f")
        printf "%-50s %6d points\n" "$(basename "$f")" "$pts"
        count=$((count + 1))
    fi
done
echo "Total files: $count"

echo ""
echo "Completed: $(date)"
