#!/bin/bash
#SBATCH --job-name=cloudcompare_normals
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G
#SBATCH --time=2:00:00
#SBATCH --output=cloudcompare_normals_%j.out
#SBATCH --error=cloudcompare_normals_%j.err

echo "=== CloudCompare Mesh Sampling with Normals ==="
echo "Started: $(date)"
echo "Job ID: ${SLURM_JOB_ID}"

cd /data/gpfs/projects/punim2657/sfs_preprocessing

module load CloudCompare/2.12.4

for piece in 01 02 03 04 05 06 07 08; do
    echo "=== Sampling Pot_A_Piece_${piece} with Normals ==="
    
    # Use CloudCompare to sample mesh and compute normals (export as ASC with normals)
    /apps/easybuild-2022/easybuild/software/MPI/GCC/11.3.0/OpenMPI/4.1.4/CloudCompare/2.12.4/bin/CloudCompare \
        -SILENT -AUTO_SAVE OFF \
        -C_EXPORT_FMT ASC -PREC 6 -SEP SPACE \
        -O Dataset/Mesh/Pot_A/Pot_A_Piece_${piece}_Mesh.obj \
        -SAMPLE_MESH DENSITY 1000000 \
        -OCTREE_NORMALS 0.5 \
        -ORIENT_NORMS_MST 6 \
        -SAVE_CLOUDS FILE "temp_piece_${piece}_with_normals.asc"
    
    # Convert ASC with normals to PCD with normals
    if [ -f "temp_piece_${piece}_with_normals.asc" ]; then
        echo "Converting ASC with normals to PCD for piece ${piece}..."
        python3 << EOF
# Read ASC file and convert to PCD with normals
import os
asc_file = "temp_piece_${piece}_with_normals.asc"
pcd_file = "Dataset/Point/Pot_A/Pot_A_Piece_${piece}_Point.pcd"

if os.path.exists(asc_file):
    with open(asc_file, 'r') as f:
        lines = f.readlines()
    
    # Filter out empty lines and comments
    data_lines = [line.strip() for line in lines if line.strip() and not line.startswith('#')]
    
    # Check if we have 6 columns (x y z nx ny nz)
    if data_lines:
        first_line_parts = data_lines[0].split()
        if len(first_line_parts) == 6:
            with open(pcd_file, 'w') as f:
                f.write('# .PCD v0.7 - Point Cloud Data file format\\n')
                f.write('VERSION 0.7\\n')
                f.write('FIELDS x y z normal_x normal_y normal_z\\n')
                f.write('SIZE 4 4 4 4 4 4\\n')
                f.write('TYPE F F F F F F\\n')
                f.write('COUNT 1 1 1 1 1 1\\n')
                f.write(f'WIDTH {len(data_lines)}\\n')
                f.write('HEIGHT 1\\n')
                f.write('VIEWPOINT 0 0 0 1 0 0 0\\n')
                f.write(f'POINTS {len(data_lines)}\\n')
                f.write('DATA ascii\\n')
                
                for line in data_lines:
                    f.write(line + '\\n')
            
            print(f"Successfully converted ASC to PCD for piece ${piece} with {len(data_lines)} points and normals")
        else:
            print(f"Warning: ASC file for piece ${piece} has {len(first_line_parts)} columns, expected 6 (x y z nx ny nz)")
    else:
        print(f"Error: No data found in ASC file for piece ${piece}")
else:
    print(f"Error: ASC file not found for piece ${piece}")
EOF
        rm -f temp_piece_${piece}_with_normals.asc
    fi
    
    if [ $? -eq 0 ]; then
        echo "✅ CloudCompare sampling with normals successful for piece ${piece}"
        
        # Check if normals were included
        if grep -q "normal" Dataset/Point/Pot_A/Pot_A_Piece_${piece}_Point.pcd; then
            echo "✅ Normals detected in PCD file for piece ${piece}"
            head -15 Dataset/Point/Pot_A/Pot_A_Piece_${piece}_Point.pcd
        else
            echo "⚠️  No normals detected in PCD file for piece ${piece}"
            head -15 Dataset/Point/Pot_A/Pot_A_Piece_${piece}_Point.pcd
        fi
        
        ls -la Dataset/Point/Pot_A/Pot_A_Piece_${piece}_Point.pcd
    else
        echo "❌ CloudCompare sampling failed for piece ${piece}"
    fi
done

echo "=== CloudCompare with normals completed at: $(date) ==="