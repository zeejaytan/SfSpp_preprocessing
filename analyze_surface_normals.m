function analyze_surface_normals()
% Analyze differences in surface normals between TPS and NURBS
% to identify what causes PotSAC matrix size mismatch

fprintf('=== SURFACE NORMALS ANALYSIS ===\n');

% NURBS surface files
nurbs_0_file = 'Temp/Data/Pot_A/Pot_A_Piece_01_Surface_0.xyz';
nurbs_1_file = 'Temp/Data/Pot_A/Pot_A_Piece_01_Surface_1.xyz';

% TPS surface files  
tps_0_file = '../TPS_Processing_Workspace/Surfaces/Pot_A_Piece_01_Surface_0.xyz';
tps_1_file = '../TPS_Processing_Workspace/Surfaces/Pot_A_Piece_01_Surface_1.xyz';

% Test with just first 100 points to isolate the issue
test_points = 100;

if exist(nurbs_0_file, 'file') && exist(tps_0_file, 'file')
    % Load data
    nurbs_data = load(nurbs_0_file);
    tps_data = load(tps_0_file);
    
    % Take small samples
    nurbs_sample = nurbs_data(1:test_points, :)';  % [6 x N]
    tps_sample = tps_data(1:test_points, :)';      % [6 x N]
    
    fprintf('NURBS sample: %dx%d\n', size(nurbs_sample, 1), size(nurbs_sample, 2));
    fprintf('TPS sample:   %dx%d\n', size(tps_sample, 1), size(tps_sample, 2));
    
    % Analyze normal vectors (rows 4-6)
    nurbs_normals = nurbs_sample(4:6, :);
    tps_normals = tps_sample(4:6, :);
    
    fprintf('\n=== NORMAL VECTOR ANALYSIS ===\n');
    
    % Check normal magnitudes
    nurbs_magnitudes = sqrt(sum(nurbs_normals.^2, 1));
    tps_magnitudes = sqrt(sum(tps_normals.^2, 1));
    
    fprintf('NURBS normal magnitudes:\n');
    fprintf('  Min: %.6f, Max: %.6f, Mean: %.6f, Std: %.6f\n', ...
           min(nurbs_magnitudes), max(nurbs_magnitudes), ...
           mean(nurbs_magnitudes), std(nurbs_magnitudes));
    
    fprintf('TPS normal magnitudes:\n');
    fprintf('  Min: %.6f, Max: %.6f, Mean: %.6f, Std: %.6f\n', ...
           min(tps_magnitudes), max(tps_magnitudes), ...
           mean(tps_magnitudes), std(tps_magnitudes));
    
    % Check for NaN or Inf values
    nurbs_nan = sum(isnan(nurbs_sample(:)) | isinf(nurbs_sample(:)));
    tps_nan = sum(isnan(tps_sample(:)) | isinf(tps_sample(:)));
    
    fprintf('\nNaN/Inf values:\n');
    fprintf('  NURBS: %d bad values\n', nurbs_nan);
    fprintf('  TPS:   %d bad values\n', tps_nan);
    
    % Test the exact PotSAC computation steps
    fprintf('\n=== TESTING POTSAC COMPUTATION STEPS ===\n');
    
    try
        fprintf('Testing TPS data...\n');
        test_pottmann_computation(tps_sample, 'TPS');
    catch tps_error
        fprintf('❌ TPS failed: %s\n', tps_error.message);
    end
    
    try
        fprintf('Testing NURBS data...\n');
        test_pottmann_computation(nurbs_sample, 'NURBS');
    catch nurbs_error
        fprintf('❌ NURBS failed: %s\n', nurbs_error.message);
    end
    
else
    fprintf('❌ Surface files not found\n');
end

fprintf('\n=== ANALYSIS COMPLETE ===\n');
end

function test_pottmann_computation(X, data_type)
% Test the exact computation that fails in compute_pottmann_axis
fprintf('  %s data shape: %dx%d\n', data_type, size(X, 1), size(X, 2));

% Step 1: euc2plucker conversion (line 10 in compute_pottmann_axis)
addpath('AxisExtraction/');
try
    X_reordered = X([4:6,1:3],:);  % Reorder: normals first, then points
    fprintf('  Reordered shape: %dx%d\n', size(X_reordered, 1), size(X_reordered, 2));
    
    J_raw = euc2plucker(X_reordered);
    fprintf('  After euc2plucker: %dx%d\n', size(J_raw, 1), size(J_raw, 2));
    
    J = J_raw([4:6,1:3],:)';  % Reorder again and transpose
    fprintf('  Final J matrix: %dx%d\n', size(J, 1), size(J, 2));
    
    % Step 2: JTJ computation
    JTJ = J'*J;
    fprintf('  JTJ matrix: %dx%d\n', size(JTJ, 1), size(JTJ, 2));
    
    % Step 3: Submatrix extraction
    M11 = JTJ(1:3,1:3);
    M12 = JTJ(1:3,4:6);
    M22 = JTJ(4:6,4:6);
    
    fprintf('  M11: %dx%d, M12: %dx%d, M22: %dx%d\n', ...
           size(M11,1), size(M11,2), size(M12,1), size(M12,2), ...
           size(M22,1), size(M22,2));
    
    % Step 4: The critical computation (line 17)
    M22_inv = M22 \ M12';
    fprintf('  M22\\M12'': %dx%d\n', size(M22_inv, 1), size(M22_inv, 2));
    
    M = (M11 - M12 * M22_inv);
    fprintf('  Final M: %dx%d\n', size(M, 1), size(M, 2));
    
    % Step 5: SVD
    [V, D] = svd(M);
    s = diag(D);
    [~, ia] = sort(s);
    v = V(:, ia(1));
    fprintf('  v vector: %dx%d\n', size(v, 1), size(v, 2));
    
    % Step 6: The failing computation (line 24-25)
    vbar = - M22 \ (M12' * v);
    fprintf('  vbar vector: %dx%d\n', size(vbar, 1), size(vbar, 2));
    
    % Step 7: The cross product that fails
    cross_result = cross(v, vbar);
    fprintf('  cross(v,vbar): %dx%d\n', size(cross_result, 1), size(cross_result, 2));
    
    vt = [v; cross_result];
    fprintf('  ✅ %s SUCCESS! Final vt: %dx%d\n', data_type, size(vt, 1), size(vt, 2));
    
catch computation_error
    fprintf('  ❌ %s FAILED at: %s\n', data_type, computation_error.message);
    
    % Print the error stack for debugging
    if ~isempty(computation_error.stack)
        fprintf('     Error location: %s:%d\n', ...
               computation_error.stack(1).name, computation_error.stack(1).line);
    end
end
end