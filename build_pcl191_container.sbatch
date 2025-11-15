#!/bin/bash
#SBATCH --job-name=pcl191_build
#SBATCH --time=2:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=16G
#SBATCH --output=pcl191_build_%j.out
#SBATCH --error=pcl191_build_%j.err

cd /data/gpfs/projects/punim2657/sfs_preprocessing

# Build PCL 1.9.1 container with NURBS support
CONTAINER_PATH="/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer"
$CONTAINER_PATH build pcl_191_nurbs.sif pcl_191_nurbs.def

echo "PCL 1.9.1 container build completed at $(date)"