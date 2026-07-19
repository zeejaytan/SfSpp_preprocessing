#!/bin/bash
#SBATCH --job-name=matlab_axis_pot_a
#SBATCH --time=02:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=8G

cd /data/gpfs/projects/punim2657/sfs_preprocessing

echo "==========================================="
echo "MATLAB Axis Extraction: Pot A (8 pieces)"
echo "==========================================="
echo "Started: $(date)"
echo ""

module load MATLAB/2024b_Update_3

# Create output directory
mkdir -p axis_output

# Process all 8 pieces
for piece_id in {01..08}; do
    echo ""
    echo "========== Processing Piece $piece_id =========="
    echo "Time: $(date)"
    
    # Create unique MATLAB script per piece
    cat > run_axis_piece_${piece_id}.m << MATLAB_EOF
addpath('/data/gpfs/projects/punim2657/sfs_preprocessing/AxisExtraction');
output_dir = '/data/gpfs/projects/punim2657/sfs_preprocessing/axis_output';

try
    fprintf('Starting axis extraction for Pot A, Piece ${piece_id}\n');
    
    % Call the main axis extraction function
    vt = extract_axis('A', ${piece_id}, false);
    
    % Save results
    output_file = sprintf('%s/Pot_A_Piece_${piece_id}_Axis.txt', output_dir);
    writematrix(vt, output_file, 'Delimiter', ' ');
    
    fprintf('✅ Axis extraction completed for Piece ${piece_id}\n');
    fprintf('📁 Results saved to: %s\n', output_file);
    fprintf('🎯 Found %d axes\n', size(vt, 2));
    
    % Display best axis
    if size(vt, 2) > 0
        fprintf('Best axis - Direction: [%.6f, %.6f, %.6f]\n', vt(1,1), vt(2,1), vt(3,1));
        fprintf('Best axis - Position:  [%.6f, %.6f, %.6f]\n', vt(4,1), vt(5,1), vt(6,1));
    end
    
    exit(0);
catch ME
    fprintf('❌ Error in axis extraction: %s\n', ME.message);
    exit(1);
end
MATLAB_EOF
    
    # Run MATLAB
    matlab -nodisplay -nosplash -nodesktop \
      -logfile "matlab_axis_pot_a_piece_${piece_id}.log" \
      -r "try, run('run_axis_piece_${piece_id}.m'); catch ME, disp(getReport(ME)); exit(1); end; exit(0);"
    
    MATLAB_EXIT_CODE=$?
    
    if [ $MATLAB_EXIT_CODE -eq 0 ]; then
        echo "✅ Piece $piece_id: SUCCESS"
    else
        echo "❌ Piece $piece_id: FAILED (exit code: $MATLAB_EXIT_CODE)"
    fi
done

echo ""
echo "========== FINAL SUMMARY =========="
echo "Axis files generated:"
ls -lh axis_output/Pot_A_Piece_*.txt 2>/dev/null | wc -l
echo ""
echo "Completed: $(date)"
