#!/bin/bash
#SBATCH --job-name=sfs_prep_robust
#SBATCH --time=02:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=16G
#SBATCH --output=sfs_prep_robust_%j.out
#SBATCH --error=sfs_prep_robust_%j.err

echo "=== SfS Preprocessing Robust Build ==="
echo "Job started at: $(date)"
echo "Using proven multi-stage approach from main SfS system"

# Set working directory
cd /data/gpfs/projects/punim2657/sfs_preprocessing

echo "Launching robust build pipeline..."
./build_preprocessing_pipeline.sh

BUILD_EXIT_CODE=$?

if [ $BUILD_EXIT_CODE -eq 0 ]; then
    echo "✅ Robust build completed successfully!"
    echo "Container info:"
    ls -lh sfs_preprocessing.sif 2>/dev/null || echo "Container file not found"
    
    echo "Testing final container:"
    module load Apptainer/1.3.3
    apptainer exec sfs_preprocessing.sif /bin/bash -c "echo 'Final container test successful'" 2>/dev/null || echo "Container test failed"
    
else
    echo "❌ Robust build failed with exit code: $BUILD_EXIT_CODE"
    echo "Check logs in: logs/"
    ls -la logs/ 2>/dev/null || echo "No logs directory found"
fi

echo ""
echo "=== Robust build completed at: $(date) ==="