#!/bin/bash
#SBATCH --job-name=juglet_matprobe2
#SBATCH --account=punim2657
#SBATCH --partition=sapphire
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=8G
#SBATCH --time=0:20:00
#SBATCH --output=juglet_matprobe2_%j.out
#SBATCH --error=juglet_matprobe2_%j.err

cd /data/gpfs/projects/punim2657/sfs_preprocessing
POT_ID="A"
POT_NAME="Juglet"
NUM_PIECES=9
OUTPUT_BASE="/data/gpfs/projects/punim2657/sfs_preprocessing/Juglet_Dataset_20260916"
module load MATLAB/2024b_Update_3
matlab -batch "
disp('MARKER-START');
addpath('.');
for piece = 1:${NUM_PIECES}
    piece_str = sprintf('%d', piece);
    surface_file = sprintf('${OUTPUT_BASE}/SfS_pp/Surfaces/${POT_NAME}_Piece_%s_Surface_0.xyz', piece_str);
    output_file = sprintf('${OUTPUT_BASE}/SfS_pp/Axes/${POT_NAME}_Piece_%s_Axis.xyz', piece_str);
    fprintf('Processing piece %s/%d...\n', piece_str, ${NUM_PIECES});
    if exist(surface_file, 'file')
        try
            extract_single_axis('${POT_ID}', piece, surface_file, output_file);
            fprintf('ok piece %s\n', piece_str);
        catch ME
            fprintf('FAILED piece %s: %s\n', piece_str, ME.message);
        end
    else
        fprintf('missing surface: %s\n', surface_file);
    end
end
fprintf('axis extraction done\n');
quit;
"
echo "matlab exit: $?"
ls ${OUTPUT_BASE}/SfS_pp/Axes/ 2>/dev/null
echo "Done: $(date)"
