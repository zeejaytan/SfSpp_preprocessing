#!/bin/bash
#SBATCH --job-name=regen_surfaces
#SBATCH --time=01:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=16G
#SBATCH --partition=sapphire
#SBATCH --output=regen_surfaces_%j.out
#SBATCH --error=regen_surfaces_%j.err

cd /data/gpfs/projects/punim2657/sfs_preprocessing

echo "Regenerating 19K surfaces..."
echo "Started: $(date)"

module load Apptainer/1.3.3

timeout 2400 apptainer exec --bind /data:/data \
  /data/gpfs/projects/punim2657/sfs_preprocessing/pcl_191_nurbs.sif \
  ./build_new/MeshPreprocessingHeadless 2>&1 | tee regen_surfaces.log

echo ""
echo "Surface counts after regeneration:"
for piece in 01 02 03 04 05 06 07 08; do
  for s in 0 1; do
    f="Temp/Data/Pot_A/Pot_A_Piece_${piece}_Surface_${s}.xyz"
    [ -f "$f" ] && echo "Piece_${piece}_S${s}: $(wc -l < "$f")"
  done
done

echo "Completed: $(date)"
