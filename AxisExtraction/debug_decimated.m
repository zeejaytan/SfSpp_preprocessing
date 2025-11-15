% Debug the decimated dataset that causes the cross product error
fprintf('=== Debugging Decimated Dataset Error ===\n');

try
    [C0, C1] = read_surfaces('A', 1, false);
    C = [C0, C1];
    num_points = size(C, 2);
    
    % Create the problematic decimated dataset
    decimated_C = C(:,1:10:num_points);
    fprintf('Decimated C size: %dx%d\n', size(decimated_C, 1), size(decimated_C, 2));
    
    % Check for data quality issues that might cause problems
    fprintf('\nData quality analysis:\n');
    fprintf('NaN count: %d\n', sum(isnan(decimated_C(:))));
    fprintf('Inf count: %d\n', sum(isinf(decimated_C(:))));
    
    % Check normal vectors
    normal_mags = sqrt(sum(decimated_C(4:6,:).^2));
    fprintf('Normal magnitudes: min=%e, max=%e, zeros=%d\n', ...
            min(normal_mags), max(normal_mags), sum(normal_mags < 1e-15));
    
    % Try compute_axis_of_symmetry step by step with debugging
    fprintf('\nStepping through compute_axis_of_symmetry...\n');
    
    % Normalize normals
    decimated_C(4:6,:) = decimated_C(4:6,:) ./ sqrt(sum(decimated_C(4:6,:).^2));
    
    % Check after normalization
    normal_mags_after = sqrt(sum(decimated_C(4:6,:).^2));
    fprintf('After normalization: min=%e, max=%e, NaN=%d\n', ...
            min(normal_mags_after), max(normal_mags_after), sum(isnan(normal_mags_after)));
    
    % Try just one iteration to catch the error
    num_sample_set = 6;
    
    for iter = 1:10  % Try a few iterations
        fprintf('\nIteration %d:\n', iter);
        
        try
            kidx = randsample(size(decimated_C, 2), num_sample_set);
            Cs = decimated_C(:, kidx);
            
            fprintf('  Sample indices: [%s]\n', num2str(kidx));
            fprintf('  Cs size: %dx%d\n', size(Cs, 1), size(Cs, 2));
            
            % Check the sample data
            fprintf('  Sample data analysis:\n');
            fprintf('    NaN: %d, Inf: %d\n', sum(isnan(Cs(:))), sum(isinf(Cs(:))));
            
            sample_normal_mags = sqrt(sum(Cs(4:6,:).^2));
            fprintf('    Normal mags: min=%e, max=%e\n', min(sample_normal_mags), max(sample_normal_mags));
            
            % Apply preprocessing
            mCs = mean(Cs(1:3,:), 2);
            Cs(1:3,:) = Cs(1:3,:) - mCs;
            scale = mean(abs(Cs(:)));
            fprintf('    Scale: %e\n', scale);
            
            if scale < 1e-15
                fprintf('    ⚠ Scale is essentially zero - points might be identical!\n');
                % Check if points are identical
                point_diffs = diff(Cs(1:3,:), 1, 2);
                max_diff = max(abs(point_diffs(:)));
                fprintf('    Max point difference: %e\n', max_diff);
            end
            
            Cs(1:3,:) = Cs(1:3,:) / scale;
            
            % Check after scaling
            fprintf('    After scaling NaN: %d, Inf: %d\n', sum(isnan(Cs(:))), sum(isinf(Cs(:))));
            
            % Try compute_pottmann_axis
            fprintf('  Calling compute_pottmann_axis...');
            vt = compute_pottmann_axis(Cs);
            fprintf(' ✓ Success!\n');
            
        catch ME
            fprintf('  ❌ ERROR: %s\n', ME.message);
            
            if contains(ME.message, 'same size')
                fprintf('  This is the cross product error!\n');
                
                % Deep dive into the failing sample
                fprintf('  Problematic sample detailed analysis:\n');
                for j = 1:size(Cs, 2)
                    pt = Cs(:, j);
                    fprintf('    Point %d: pos=[%f,%f,%f] norm=[%f,%f,%f]\n', j, ...
                            pt(1), pt(2), pt(3), pt(4), pt(5), pt(6));
                end
                
                return; % Stop at first error
            end
        end
    end
    
    fprintf('\nNo error found in first 10 iterations - might be a rare occurrence\n');
    
catch ME
    fprintf('❌ Setup error: %s\n', ME.message);
end