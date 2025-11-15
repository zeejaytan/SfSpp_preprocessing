% Trace run_potsac function completely to find the cross product error
fprintf('=== Tracing run_potsac Function Completely ===\n');

try
    % Step 1: Read surfaces exactly as extract_axis does
    fprintf('Step 1: Reading surfaces...\n');
    [C0, C1] = read_surfaces('A', 1, false);
    
    % Step 2: Call run_potsac exactly as extract_axis does
    fprintf('Step 2: Calling run_potsac with data subsets...\n');
    
    % This replicates extract_axis.m line 8
    fprintf('C0 original size: %dx%d, C1 original size: %dx%d\n', size(C0,1), size(C0,2), size(C1,1), size(C1,2));
    
    % run_potsac is called with C0(:,1:1:end), C1(:,1:1:end)
    % which is just C0, C1 (the :1:end does nothing)
    
    % Step into run_potsac manually
    C1_input = C0(:,1:1:end);  % This is just C0
    C2_input = C1(:,1:1:end);  % This is just C1
    
    fprintf('Inputs to run_potsac: C1_input=%dx%d, C2_input=%dx%d\n', ...
            size(C1_input,1), size(C1_input,2), size(C2_input,1), size(C2_input,2));
    
    % Manual implementation of run_potsac
    C = [C1_input, C2_input];
    num_points = size(C, 2);
    fprintf('Combined C size: %dx%d, num_points: %d\n', size(C,1), size(C,2), num_points);
    
    % Step 3: First compute_axis_of_symmetry call
    fprintf('Step 3: Calling compute_axis_of_symmetry (decimated)...\n');
    decimated_C = C(:,1:10:num_points);  % This is the 1:10:end decimation
    fprintf('Decimated C size: %dx%d\n', size(decimated_C,1), size(decimated_C,2));
    
    try
        [vt, ~, costs] = compute_axis_of_symmetry(decimated_C);
        fprintf('✓ compute_axis_of_symmetry successful, vt size: %dx%d\n', size(vt,1), size(vt,2));
    catch ME
        fprintf('❌ ERROR in compute_axis_of_symmetry: %s\n', ME.message);
        return;
    end
    
    % Step 4: Refine axes loop
    fprintf('Step 4: Refining axes...\n');
    num_candidates = 10;
    vt = vt(:, 1:min(num_candidates, size(vt, 2)));
    
    for i = 1 : size(vt, 2)
        try
            fprintf('  Refining axis %d/%d...\n', i, size(vt, 2));
            vt(:,i) = refine_axis(vt(:,i), C(:,1:10:end), 2, [], [], 300, 1e-3);
        catch ME
            fprintf('❌ ERROR in refine_axis iteration %d: %s\n', i, ME.message);
            return;
        end
    end
    
    % Step 5: Cost computation loop  
    fprintf('Step 5: Computing costs...\n');
    robustifier = @robustifier_huber;
    cost = nan(size(vt, 2), 1);
    for i = 1 : size(vt, 2)
        try
            fprintf('  Computing cost for axis %d/%d...\n', i, size(vt, 2));
            residual = compute_biaxial_cao_error(vt(:,i), C(:,1:10:end));
            cost(i) = sum(apply_robustifier(robustifier, residual));
        catch ME
            fprintf('❌ ERROR in cost computation iteration %d: %s\n', i, ME.message);
            return;
        end
    end
    
    % Step 6: Final refinement loop
    fprintf('Step 6: Final refinement with full dataset...\n');
    
    % Filter similar axes and high costs (simplified)
    unique_axes = 1:size(vt, 2);  % Simplified - skip the angle filtering for now
    
    for i = 1 : length(unique_axes)
        try
            fprintf('  Final refinement %d/%d...\n', i, length(unique_axes));
            vt(:,unique_axes(i)) = refine_axis(vt(:,unique_axes(i)), C, 2, [], [], 300, 1e-9);
        catch ME
            fprintf('❌ ERROR in final refine_axis iteration %d: %s\n', i, ME.message);
            
            % This might be where the error occurs - with the full dataset C
            fprintf('Full dataset C size: %dx%d\n', size(C, 1), size(C, 2));
            
            return;
        end
    end
    
    fprintf('✓ All steps in run_potsac completed successfully!\n');
    
catch ME
    fprintf('❌ Overall error: %s\n', ME.message);
    
    % Print detailed stack trace
    fprintf('\nStack trace:\n');
    for i = 1:length(ME.stack)
        fprintf('  File: %s\n', ME.stack(i).file);
        fprintf('  Function: %s\n', ME.stack(i).name);
        fprintf('  Line: %d\n', ME.stack(i).line);
        fprintf('  ---\n');
    end
end