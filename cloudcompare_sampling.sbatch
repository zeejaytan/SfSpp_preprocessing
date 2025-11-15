#!/bin/bash
#SBATCH --job-name=cloudcompare_sampling
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --array=1-8
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=48G
#SBATCH --time=1:30:00
#SBATCH --output=cloudcompare_sampling_%A_%a.out
#SBATCH --error=cloudcompare_sampling_%A_%a.err

echo "=== CloudCompare Mesh Sampling ==="
echo "Started: $(date)"
echo "Job ID: ${SLURM_JOB_ID}"
echo "Array Task ID: ${SLURM_ARRAY_TASK_ID}"

cd /data/gpfs/projects/punim2657/sfs_preprocessing

module load CloudCompare/2.12.4

# Convert array task ID to piece number with zero padding
piece=$(printf "%02d" ${SLURM_ARRAY_TASK_ID})
    echo "=== Sampling Pot_A_Piece_${piece} ==="
    
    # Try CloudCompare mesh sampling with normals
    timeout 120 /apps/easybuild-2022/easybuild/software/MPI/GCC/11.3.0/OpenMPI/4.1.4/CloudCompare/2.12.4/bin/CloudCompare \
        -SILENT -AUTO_SAVE OFF \
        -O NURBS_Dataset_20250831/SfS_pp/Mesh/Pot_A_Piece_${piece}_Mesh.obj \
        -SAMPLE_MESH DENSITY 1000000 \
        -C_EXPORT_FMT ASC \
        -SAVE_CLOUDS FILE "Pot_A_Piece_${piece}_Mesh_SAMPLED_POINTS.asc"
    
    if [ $? -eq 0 ]; then
        echo "✅ CloudCompare sampling successful for piece ${piece}"
        ls -la Pot_A_Piece_${piece}_Mesh_SAMPLED_POINTS.asc
        
        # Convert ASC to PCD format for pipeline compatibility
        if [ -f "Pot_A_Piece_${piece}_Mesh_SAMPLED_POINTS.asc" ]; then
            python3 -c "
import os
asc_file = 'Pot_A_Piece_${piece}_Mesh_SAMPLED_POINTS.asc'
pcd_file = 'Dataset/Point/Pot_A/Pot_A_Piece_${piece}_Point.pcd'
os.makedirs('Dataset/Point/Pot_A', exist_ok=True)

points = []
with open(asc_file, 'r') as f:
    for line in f:
        parts = line.strip().split()
        if len(parts) >= 6:
            x, y, z, nx, ny, nz = map(float, parts[:6])
            points.append([x, y, z, nx, ny, nz])

with open(pcd_file, 'w') as f:
    f.write('# .PCD v0.7 - Point Cloud Data file format\n')
    f.write('VERSION 0.7\n')
    f.write('FIELDS x y z normal_x normal_y normal_z\n')
    f.write('SIZE 4 4 4 4 4 4\n')
    f.write('TYPE F F F F F F\n')
    f.write('COUNT 1 1 1 1 1 1\n')
    f.write(f'WIDTH {len(points)}\n')
    f.write('HEIGHT 1\n')
    f.write('VIEWPOINT 0 0 0 1 0 0 0\n')
    f.write(f'POINTS {len(points)}\n')
    f.write('DATA ascii\n')
    for point in points:
        f.write(f'{point[0]:.6f} {point[1]:.6f} {point[2]:.6f} {point[3]:.6f} {point[4]:.6f} {point[5]:.6f}\n')
print(f'Converted {len(points)} points to {pcd_file}')
"
        fi
    else
        echo "❌ CloudCompare sampling FAILED for piece ${piece}"
        echo "Error code: $?"
    fi

echo "=== CloudCompare sampling completed for piece ${piece} at: $(date) ==="