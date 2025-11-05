function test_nurbs_simple()
% Simple test to isolate NURBS PotSAC error
fprintf('=== SIMPLE NURBS TEST ===\n');

try
    % Test with very small NURBS sample (should work based on earlier tests)
    nurbs_0_file = 'Temp/Data/Pot_A/Pot_A_Piece_01_Surface_0.xyz';
    
    if ~exist(nurbs_0_file, 'file')
        fprintf('❌ File not found: %s\n', nurbs_0_file);
        return;
    end
    
    % Load small sample
    nurbs_data = load(nurbs_0_file);
    sample_size = 1000;  % Small enough that it should work
    nurbs_sample = nurbs_data(1:sample_size, :);
    
    fprintf('Sample size: %d points\n', sample_size);
    
    % Split into points and normals like working TPS version
    points = nurbs_sample(:, 1:3);
    normals = nurbs_sample(:, 4:6);
    
    % Create combined data like TPS version
    C_data = [points, normals]';
    fprintf('C_data format: %dx%d\n', size(C_data, 1), size(C_data, 2));
    
    % Test PotSAC
    addpath('AxisExtraction/');
    axis_result = run_potsac(C_data);
    
    fprintf('✅ SUCCESS! NURBS axis extraction worked with %d points\n', sample_size);
    fprintf('   Result: %dx%d\n', size(axis_result, 1), size(axis_result, 2));
    
catch test_error
    fprintf('❌ FAILED: %s\n', test_error.message);
    
    % Print full stack trace for debugging
    if ~isempty(test_error.stack)
        fprintf('Stack trace:\n');
        for i = 1:length(test_error.stack)
            fprintf('  %s:%d in %s\n', test_error.stack(i).file, ...
                   test_error.stack(i).line, test_error.stack(i).name);
        end
    end
end

fprintf('=== TEST COMPLETE ===\n');
end