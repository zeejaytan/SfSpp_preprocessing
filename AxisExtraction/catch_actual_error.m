% Try to catch the actual error by running the real compute_axis_of_symmetry
fprintf('=== Attempting to Catch Actual Cross Product Error ===\n');

try
    [C0, C1] = read_surfaces('A', 1, false);
    C = [C0, C1];
    decimated_C = C(:,1:10:size(C,2));
    
    fprintf('Decimated C size: %dx%d\n', size(decimated_C, 1), size(decimated_C, 2));
    
    % Run multiple attempts to catch the intermittent error
    for attempt = 1:20
        fprintf('\nAttempt %d: Calling compute_axis_of_symmetry...\n', attempt);
        
        try
            % Set random seed for reproducibility of errors
            rng(attempt * 12345);  % Different seed each attempt
            
            [vt, num_inliers, combined_err] = compute_axis_of_symmetry(decimated_C);
            fprintf('  ✓ Success! vt size: %dx%d\n', size(vt, 1), size(vt, 2));
            
        catch ME
            fprintf('  ❌ ERROR: %s\n', ME.message);
            
            if contains(ME.message, 'same size')
                fprintf('  *** CAUGHT THE CROSS PRODUCT ERROR! ***\n');
                fprintf('  Random seed: %d\n', attempt * 12345);
                
                % Print stack trace to see exactly where it failed
                fprintf('\n  Stack trace:\n');
                for i = 1:length(ME.stack)
                    fprintf('    File: %s\n', ME.stack(i).file);
                    fprintf('    Function: %s\n', ME.stack(i).name);
                    fprintf('    Line: %d\n', ME.stack(i).line);
                    fprintf('    ---\n');
                end
                
                % Now reproduce with this specific seed for deeper investigation
                fprintf('\n  Reproducing error with seed %d for investigation...\n', attempt * 12345);
                rng(attempt * 12345);
                
                % Step through compute_axis_of_symmetry manually
                C_test = decimated_C;
                C_test(4:6,:) = C_test(4:6,:) ./ sqrt(sum(C_test(4:6,:).^2));
                num_points = size(C_test,2);
                num_sample_set = 6;
                
                % Get the exact same random sample that caused the error
                kidx = randsample(num_points, num_sample_set);
                fprintf('  Problematic sample indices: [%s]\n', num2str(kidx));
                
                % Check if indices are valid
                max_idx = max(kidx);
                if max_idx > size(C_test, 2)
                    fprintf('  *** FOUND THE ISSUE: Sample index %d exceeds dataset size %d! ***\n', ...
                            max_idx, size(C_test, 2));
                else
                    fprintf('  All indices are valid (max=%d, dataset size=%d)\n', max_idx, size(C_test, 2));
                    
                    % Extract the problematic sample
                    Cs = C_test(:, kidx);
                    fprintf('  Problematic Cs size: %dx%d\n', size(Cs, 1), size(Cs, 2));
                    
                    % Try to isolate where in compute_pottmann_axis it fails
                    try
                        mCs = mean(Cs(1:3,:), 2);
                        Cs(1:3,:) = Cs(1:3,:) - mCs;
                        scale = mean(abs(Cs(:)));
                        Cs(1:3,:) = Cs(1:3,:) / scale;
                        vt = compute_pottmann_axis(Cs);
                    catch ME2
                        fprintf('  Error reproduced: %s\n', ME2.message);
                    end
                end
                
                return; % Stop after catching the first error
            else
                fprintf('  Different error - continuing...\n');
            end
        end
    end
    
    fprintf('\nNo cross product error found in %d attempts\n', 20);
    
catch ME
    fprintf('❌ Setup error: %s\n', ME.message);
end