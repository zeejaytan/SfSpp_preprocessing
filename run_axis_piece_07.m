addpath('/data/gpfs/projects/punim2657/sfs_preprocessing/AxisExtraction');
output_dir = '/data/gpfs/projects/punim2657/sfs_preprocessing/axis_output';

try
    fprintf('Starting axis extraction for Pot A, Piece 07\n');
    
    % Call the main axis extraction function
    vt = extract_axis('A', 07, false);
    
    % Save results
    output_file = sprintf('%s/Pot_A_Piece_07_Axis.txt', output_dir);
    writematrix(vt, output_file, 'Delimiter', ' ');
    
    fprintf('✅ Axis extraction completed for Piece 07\n');
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
