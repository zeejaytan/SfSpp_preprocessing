#!/bin/bash
#SBATCH --job-name=test_downsampling_13k
#SBATCH --time=00:20:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=8G

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

# Build in container with cmake
apptainer exec --bind /data:/data /data/gpfs/projects/punim2657/sfs_preprocessing/pcl_191_nurbs.sif bash << 'INNER'
cd /data/gpfs/projects/punim2657/sfs_preprocessing/build
cmake .. -DCMAKE_BUILD_TYPE=Release
make -j4
INNER

# Run mesh preprocessing
echo ""
echo "Running MeshPreprocessingHeadless..."
cd /data/gpfs/projects/punim2657/sfs_preprocessing
apptainer exec --bind /data:/data /data/gpfs/projects/punim2657/sfs_preprocessing/pcl_191_nurbs.sif ./build/MeshPreprocessingHeadless 2>&1 | tail -100

# Check result point counts
echo ""
echo "=== POINT COUNT RESULTS (TEST 1: target 13K) ==="
for f in Dataset/Surfaces/Pot_A/Pot_A_Piece_*_Surface_*.xyz; do
    if [ -f "$f" ]; then
        count=$(wc -l < "$f")
        basename "$f"
        echo "  Points: $count"
    fi
done | paste - - | column -t

echo "Completed: $(date)"
