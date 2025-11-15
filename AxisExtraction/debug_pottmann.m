% Debug script to diagnose cross product error in compute_pottmann_axis
fprintf('=== Debugging compute_pottmann_axis Cross Product Error ===\n');

try
    % Get test data
    [C0, C1] = read_surfaces('A', 1, false);
    
    % Create combined surface data (same as used in compute_axis_of_symmetry)
    C = [C0, C1];
    
    % Normalize normals as done in compute_axis_of_symmetry 
    C(4:6,:) = C(4:6,:) ./ sqrt(sum(C(4:6,:).^2));
    
    % Take a sample as done in the main algorithm
    num_sample_set = 6;
    kidx = randsample(size(C, 2), num_sample_set);
    Cs = C(:, kidx);
    
    fprintf('Sample data Cs size: %dx%d\n', size(Cs, 1), size(Cs, 2));
    
    % Apply same preprocessing as compute_axis_of_symmetry
    mCs = mean(Cs(1:3,:), 2);
    Cs(1:3,:) = Cs(1:3,:) - mCs;
    scale = mean(abs(Cs(:)));
    Cs(1:3,:) = Cs(1:3,:) / scale;
    
    fprintf('After preprocessing, Cs size: %dx%d\n', size(Cs, 1), size(Cs, 2));
    fprintf('mCs size: %dx%d, scale: %f\n', size(mCs, 1), size(mCs, 2), scale);
    
    % Now step through compute_pottmann_axis manually
    fprintf('\n--- Stepping through compute_pottmann_axis ---\n');
    X = Cs;
    fprintf('X size: %dx%d\n', size(X, 1), size(X, 2));
    
    % Step 1: Create input for euc2plucker
    input_for_euc2plucker = X([4:6,1:3],:);
    fprintf('Input for euc2plucker size: %dx%d\n', size(input_for_euc2plucker, 1), size(input_for_euc2plucker, 2));
    
    % Step 2: Call euc2plucker
    J_temp = euc2plucker(input_for_euc2plucker);
    fprintf('J_temp from euc2plucker size: %dx%d\n', size(J_temp, 1), size(J_temp, 2));
    
    % Step 3: Reorder and transpose
    J = J_temp([4:6,1:3],:)';
    fprintf('J after reorder and transpose size: %dx%d\n', size(J, 1), size(J, 2));
    
    % Step 4: Compute JTJ
    JTJ = J'*J;
    fprintf('JTJ size: %dx%d\n', size(JTJ, 1), size(JTJ, 2));
    
    % Step 5: Extract submatrices
    M11 = JTJ(1:3,1:3);
    M12 = JTJ(1:3,4:6);
    M22 = JTJ(4:6,4:6);
    fprintf('M11 size: %dx%d, M12 size: %dx%d, M22 size: %dx%d\n', ...
            size(M11,1), size(M11,2), size(M12,1), size(M12,2), size(M22,1), size(M22,2));
    
    % Step 6: Compute M
    M = (M11 - M12 * (M22 \ M12'));
    fprintf('M size: %dx%d\n', size(M, 1), size(M, 2));
    
    % Step 7: SVD
    [V, D] = svd(M);
    s = diag(D);
    [~, ia] = sort(s);
    v = V(:, ia(1));
    fprintf('v size: %dx%d\n', size(v, 1), size(v, 2));
    
    % Step 8: Compute vbar
    vbar = - M22 \ (M12' * v);
    fprintf('vbar size: %dx%d\n', size(vbar, 1), size(vbar, 2));
    
    % Step 9: The problematic cross product
    fprintf('\n--- Testing cross product ---\n');
    fprintf('v size: %dx%d, vbar size: %dx%d\n', size(v, 1), size(v, 2), size(vbar, 1), size(vbar, 2));
    
    % Check if both are 3x1 vectors
    if size(v, 1) == 3 && size(v, 2) == 1 && size(vbar, 1) == 3 && size(vbar, 2) == 1
        fprintf('Both v and vbar are 3x1 vectors - cross product should work\n');
        cross_result = cross(v, vbar);
        fprintf('Cross product successful! Result size: %dx%d\n', size(cross_result, 1), size(cross_result, 2));
    else
        fprintf('ERROR: v and vbar are not both 3x1 vectors!\n');
        fprintf('v dimensions: [%s], vbar dimensions: [%s]\n', num2str(size(v)), num2str(size(vbar)));
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