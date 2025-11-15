#!/bin/bash
#SBATCH --job-name=pcd_with_normals
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=2:00:00
#SBATCH --output=pcd_with_normals_%j.out
#SBATCH --error=pcd_with_normals_%j.err

echo "=== Generate PCD Files with Normals ==="
echo "Started: $(date)"
echo "Job ID: ${SLURM_JOB_ID}"

cd /data/gpfs/projects/punim2657/sfs_preprocessing

# Use PCL container to generate PCD files with normals
CONTAINER_PATH="/apps/easybuild-2022/easybuild/software/Compiler/GCCcore/11.3.0/Apptainer/1.3.3/bin/apptainer"

for piece in 01 02 03 04 05 06 07 08; do
    echo "=== Processing Pot_A_Piece_${piece} ==="
    
    # Use PCL to load mesh, sample points, and compute normals
    $CONTAINER_PATH exec --bind /data/gpfs/projects/punim2657/sfs_preprocessing:/workspace \
        pcl_191_nurbs.sif /bin/bash -c "
cd /workspace
python3 << 'EOF'
import numpy as np
import open3d as o3d

# Load mesh
print('Loading mesh for piece ${piece}...')
mesh_file = 'Dataset/Mesh/Pot_A/Pot_A_Piece_${piece}_Mesh.obj'
mesh = o3d.io.read_triangle_mesh(mesh_file)

# Sample points from mesh (up to 1,000,000 points as per README)
print('Sampling points from mesh...')
num_points = min(1000000, len(mesh.vertices) * 3)  # Sample densely
pcd = mesh.sample_points_uniformly(number_of_points=num_points)

# Compute normals
print('Computing normals...')
pcd.estimate_normals()

# Convert to numpy arrays
points = np.asarray(pcd.points)
normals = np.asarray(pcd.normals)

# Create PCD file with normals
pcd_file = 'Dataset/Point/Pot_A/Pot_A_Piece_${piece}_Point.pcd'
print(f'Writing {len(points)} points with normals to {pcd_file}')

with open(pcd_file, 'w') as f:
    f.write('# .PCD v0.7 - Point Cloud Data file format\\n')
    f.write('VERSION 0.7\\n')
    f.write('FIELDS x y z normal_x normal_y normal_z\\n')
    f.write('SIZE 4 4 4 4 4 4\\n')
    f.write('TYPE F F F F F F\\n')
    f.write('COUNT 1 1 1 1 1 1\\n')
    f.write(f'WIDTH {len(points)}\\n')
    f.write('HEIGHT 1\\n')
    f.write('VIEWPOINT 0 0 0 1 0 0 0\\n')
    f.write(f'POINTS {len(points)}\\n')
    f.write('DATA ascii\\n')
    
    for i in range(len(points)):
        px, py, pz = points[i]
        nx, ny, nz = normals[i]
        f.write(f'{px:.6f} {py:.6f} {pz:.6f} {nx:.6f} {ny:.6f} {nz:.6f}\\n')

print(f'Successfully created PCD file for piece ${piece} with {len(points)} points and normals')
EOF
"
    
    if [ $? -eq 0 ]; then
        echo "✅ Successfully generated PCD with normals for piece ${piece}"
        ls -la Dataset/Point/Pot_A/Pot_A_Piece_${piece}_Point.pcd
    else
        echo "❌ Failed to generate PCD with normals for piece ${piece}"
    fi
done

echo "=== PCD with normals generation completed at: $(date) ==="