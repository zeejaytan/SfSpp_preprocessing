% Add AxisExtraction directory to path
addpath('/data/gpfs/projects/punim2657/sfs_preprocessing/AxisExtraction');

% Set output directory
output_dir = '/data/gpfs/projects/punim2657/sfs_preprocessing/axis_output';

% Run axis extraction
try
    fprintf('Starting axis extraction for Pot %s, Fragment %d\n', 'A', 23);
    
    % Call the main axis extraction function
    vt = extract_axis('A', 23, false);
    
    % Save results
    output_file = sprintf('%s/Pot_%s_Piece_%02d_Axis.txt', output_dir, 'A', 23);
    writematrix(vt, output_file, 'Delimiter', ' ');
    
    fprintf('✅ Axis extraction completed successfully\n');
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
