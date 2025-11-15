% Test compute_pottmann_axis directly to reproduce the exact error
fprintf('=== Testing compute_pottmann_axis Directly ===\n');

try
    % Get test data exactly as used in the pipeline
    [C0, C1] = read_surfaces('A', 1, false);
    C = [C0, C1];
    C(4:6,:) = C(4:6,:) ./ sqrt(sum(C(4:6,:).^2));
    
    % Test with different sample sizes to find the problematic case
    sample_sizes = [6, 10, 20, 100];
    
    for i = 1:length(sample_sizes)
        num_sample_set = sample_sizes(i);
        fprintf('\nTesting with sample size: %d\n', num_sample_set);
        
        % Try multiple random samples
        for trial = 1:5
            try
                kidx = randsample(size(C, 2), num_sample_set);
                Cs = C(:, kidx);
                mCs = mean(Cs(1:3,:), 2);
                Cs(1:3,:) = Cs(1:3,:) - mCs;
                scale = mean(abs(Cs(:)));
                Cs(1:3,:) = Cs(1:3,:) / scale;
                
                fprintf('  Trial %d: Calling compute_pottmann_axis...', trial);
                vt = compute_pottmann_axis(Cs);
                fprintf(' Success! vt size: %dx%d\n', size(vt, 1), size(vt, 2));
                
            catch ME
                fprintf(' ERROR: %s\n', ME.message);
                
                % If this is the cross product error, investigate further
                if contains(ME.message, 'same size')
                    fprintf('    This is the cross product error!\n');
                    fprintf('    Cs size: %dx%d\n', size(Cs, 1), size(Cs, 2));
                    
                    % Check the specific data that causes the issue
                    fprintf('    Investigating problematic data...\n');
                    fprintf('    Cs has NaN: %d, Inf: %d\n', sum(isnan(Cs(:))), sum(isinf(Cs(:))));
                    
                    % Check if normals are zero
                    normal_mags = sqrt(sum(Cs(4:6,:).^2));
                    fprintf('    Normal magnitudes: min=%f, max=%f, zeros=%d\n', ...
                            min(normal_mags), max(normal_mags), sum(normal_mags < 1e-10));
                end
                return;  % Stop at first error to diagnose
            end
        end
    end
    
    fprintf('\nAll tests passed - error might be intermittent or data-dependent\n');
    
catch ME
    fprintf('❌ Setup error: %s\n', ME.message);
end