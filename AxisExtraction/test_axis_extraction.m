% Test complete axis extraction pipeline to identify actual error location
fprintf('=== Testing Complete Axis Extraction Pipeline ===\n');

try 
    % Test with Pot A, Piece 1
    pot_id = 'A';
    frag_id = 1;
    
    fprintf('Step 1: Reading surfaces for Pot %s, Piece %d\n', pot_id, frag_id);
    [C0, C1] = read_surfaces(pot_id, frag_id, false);
    fprintf('✓ Surfaces loaded: C0=%dx%d, C1=%dx%d\n', size(C0,1), size(C0,2), size(C1,1), size(C1,2));
    
    fprintf('Step 2: Creating line_euc format\n');
    line_euc = [C0(1:3,:); C1(1:3,:)];  % Combine position vectors
    fprintf('✓ line_euc created: %dx%d\n', size(line_euc,1), size(line_euc,2));
    
    fprintf('Step 3: Converting to Plucker coordinates\n');
    line_plucker = euc2plucker(line_euc, true);
    fprintf('✓ Plucker conversion successful: %dx%d\n', size(line_plucker,1), size(line_plucker,2));
    
    fprintf('Step 4: Testing POTSAC algorithm (this might be where error occurs)\n');
    % This is likely where the actual error happens - in the POTSAC fitting
    
    % Initialize parameters for POTSAC
    parameters.min_inlier = 0.3;  % Minimum inlier ratio
    parameters.max_iteration = 1000;  % Maximum iterations
    parameters.distance_threshold = 5.0;  % Distance threshold
    
    fprintf('Running POTSAC with %d lines...\n', size(line_plucker, 2));
    
    % Check if potsac function exists and call it
    if exist('potsac', 'file')
        [parameters, inliers] = potsac(line_plucker, parameters);
        fprintf('✓ POTSAC completed successfully\n');
        fprintf('  - Inlier count: %d\n', length(inliers));
        fprintf('  - Inlier ratio: %.3f\n', length(inliers)/size(line_plucker,2));
    else
        fprintf('⚠ potsac function not found - this might be the missing piece\n');
        
        % Try to locate potsac function
        fprintf('Searching for potsac function...\n');
        search_result = which('potsac');
        if isempty(search_result)
            fprintf('❌ potsac function not in MATLAB path\n');
        else
            fprintf('Found potsac at: %s\n', search_result);
        end
    end
    
catch ME
    fprintf('❌ Error occurred: %s\n', ME.message);
    fprintf('Error identifier: %s\n', ME.identifier);
    
    % Print detailed stack trace
    fprintf('\nStack trace:\n');
    for i = 1:length(ME.stack)
        fprintf('  File: %s\n', ME.stack(i).file);
        fprintf('  Function: %s\n', ME.stack(i).name);
        fprintf('  Line: %d\n', ME.stack(i).line);
        fprintf('  ---\n');
    end
end

fprintf('=== Test Complete ===\n');