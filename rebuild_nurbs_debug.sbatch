#!/bin/bash
#SBATCH --job-name=rebuild_nurbs
#SBATCH --time=00:30:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --partition=sapphire

echo "=== Rebuilding NURBS MeshPreprocessingHeadless with Debug Logging ==="
echo "Started: $(date)"

cd /data/gpfs/projects/punim2657/sfs_preprocessing

CONTAINER_PATH="/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer"

echo "Rebuilding MeshPreprocessingHeadless..."
$CONTAINER_PATH exec --bind /data/gpfs/projects/punim2657/sfs_preprocessing:/workspace \
    pcl_191_nurbs.sif /bin/bash -c \
    "cd /workspace/original_nurbs_preprocessing/build && make MeshPreprocessingHeadless"

if [ $? -eq 0 ]; then
    echo "Rebuild successful!"
    ls -lh original_nurbs_preprocessing/build/MeshPreprocessingHeadless
else
    echo "Rebuild failed!"
    exit 1
fi

echo "Completed: $(date)"
