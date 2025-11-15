% Trace the complete pipeline step by step to find where cross product error occurs
fprintf('=== Tracing Complete Pipeline for Cross Product Error ===\n');

try
    % Step 1: Read surfaces  
    fprintf('Step 1: Reading surfaces...\n');
    [C0, C1] = read_surfaces('A', 1, false);
    fprintf('✓ Surfaces read successfully\n');
    
    % Step 2: Run full extract_axis but with detailed tracing
    fprintf('Step 2: Starting extract_axis (run_potsac)...\n');
    
    % Manual implementation of run_potsac with tracing
    if false  % Skip this for now - we know the issue is in compute_axis_of_symmetry
        num_points = size(C0, 2);
        C1_sub = C0(:,1:(0.5*num_points));
        C2_sub = C0(:,(0.5*num_points):1:num_points);
        C = [C1_sub, C2_sub];
    else
        C = [C0, C1]; % This matches extract_axis.m line 8
    end
    
    fprintf('Combined C size: %dx%d\n', size(C, 1), size(C, 2));
    
    % Step 3: Call compute_axis_of_symmetry with detailed tracing
    fprintf('Step 3: Calling compute_axis_of_symmetry...\n');
    
    % Manually implement compute_axis_of_symmetry to trace the error
    % Normalize normals
    C(4:6,:) = C(4:6,:) ./ sqrt(sum(C(4:6,:).^2));
    
    num_points = size(C,2);
    num_sample_set = 6;
    max_iters = 1000;
    inlier_threshold = 1.0;
    
    fprintf('Starting RANSAC loop with %d iterations...\n', max_iters);
    
    for iter = 1 : max_iters
        if mod(iter, 100) == 0
            fprintf('  Iteration %d/%d\n', iter, max_iters);
        end
        
        try
            kidx = randsample(num_points, num_sample_set);
            Cs = C(:,kidx);
            mCs = mean(Cs(1:3,:), 2);
            Cs(1:3,:) = Cs(1:3,:) - mCs;
            scale = mean(abs(Cs(:)));
            Cs(1:3,:) = Cs(1:3,:) / scale;
            
            % This is where the error likely occurs
            vt_iter = compute_pottmann_axis(Cs);
            
        catch ME
            fprintf('❌ ERROR at iteration %d: %s\n', iter, ME.message);
            fprintf('Random sample indices: [%s]\n', num2str(kidx));
            fprintf('Cs size: %dx%d\n', size(Cs, 1), size(Cs, 2));
            
            % Check the problematic data
            fprintf('Cs data analysis:\n');
            fprintf('  NaN count: %d\n', sum(isnan(Cs(:))));
            fprintf('  Inf count: %d\n', sum(isinf(Cs(:))));
            fprintf('  Scale value: %f\n', scale);
            
            % Check normal magnitudes before scaling
            normal_mags = sqrt(sum(C(4:6,kidx).^2));
            fprintf('  Original normal magnitudes: min=%e, max=%e, zeros=%d\n', ...
                    min(normal_mags), max(normal_mags), sum(normal_mags < 1e-15));
            
            % Check if any points are identical
            point_diffs = diff(Cs(1:3,:), 1, 2);
            zero_diffs = sum(sum(abs(point_diffs) < 1e-15, 1) == 3);
            fprintf('  Identical points: %d\n', zero_diffs);
            
            return; % Stop at first error
        end
    end
    
    fprintf('✓ All %d iterations completed successfully\n', max_iters);
    
catch ME
    fprintf('❌ Pipeline error: %s\n', ME.message);
    
    % Print detailed stack trace
    fprintf('\nStack trace:\n');
    for i = 1:length(ME.stack)
        fprintf('  File: %s\n', ME.stack(i).file);
        fprintf('  Function: %s\n', ME.stack(i).name);
        fprintf('  Line: %d\n', ME.stack(i).line);
        fprintf('  ---\n');
    end
end