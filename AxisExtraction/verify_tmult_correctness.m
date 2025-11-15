% Verify if tmult implementation is mathematically correct for the axis extraction context
fprintf('=== Verifying tmult Mathematical Correctness ===\n');

try
    % Test with simple known case to verify tensor multiplication semantics
    
    % Test 1: Simple 2D case (should work like regular matrix multiplication)
    A_2d = [1 2; 3 4];
    B_2d = [5 6; 7 8];
    
    expected_2d = A_2d * B_2d;
    result_2d = tmult(A_2d, B_2d);
    
    fprintf('Test 1 - 2D Matrix Multiplication:\n');
    fprintf('Expected: [%s; %s]\n', num2str(expected_2d(1,:)), num2str(expected_2d(2,:)));
    fprintf('tmult:    [%s; %s]\n', num2str(result_2d(1,:)), num2str(result_2d(2,:)));
    fprintf('Match: %s\n\n', mat2str(isequal(expected_2d, result_2d)));
    
    % Test 2: Transpose functionality
    expected_2d_t = A_2d' * B_2d;
    result_2d_t = tmult(A_2d, B_2d, true);
    
    fprintf('Test 2 - 2D with Transpose:\n');
    fprintf('Expected A^T * B: [%s; %s]\n', num2str(expected_2d_t(1,:)), num2str(expected_2d_t(2,:)));
    fprintf('tmult(A,B,true):  [%s; %s]\n', num2str(result_2d_t(1,:)), num2str(result_2d_t(2,:)));
    fprintf('Match: %s\n\n', mat2str(isequal(expected_2d_t, result_2d_t)));
    
    % Test 3: 3D tensor case (critical for Jacobian computation)
    % Create simple 3D tensors
    A_3d = zeros(2, 3, 2);
    A_3d(:,:,1) = [1 2 3; 4 5 6];
    A_3d(:,:,2) = [7 8 9; 10 11 12];
    
    B_3d = zeros(3, 2, 2);
    B_3d(:,:,1) = [1 2; 3 4; 5 6];
    B_3d(:,:,2) = [7 8; 9 10; 11 12];
    
    result_3d = tmult(A_3d, B_3d);
    
    % Manual computation for verification
    expected_3d = zeros(2, 2, 2);
    expected_3d(:,:,1) = A_3d(:,:,1) * B_3d(:,:,1);
    expected_3d(:,:,2) = A_3d(:,:,2) * B_3d(:,:,2);
    
    fprintf('Test 3 - 3D Tensor Multiplication:\n');
    fprintf('tmult result slice 1: [%s; %s]\n', num2str(result_3d(:,:,1), 2));
    fprintf('Expected slice 1:     [%s; %s]\n', num2str(expected_3d(:,:,1), 2));
    fprintf('tmult result slice 2: [%s; %s]\n', num2str(result_3d(:,:,2), 2));
    fprintf('Expected slice 2:     [%s; %s]\n', num2str(expected_3d(:,:,2), 2));
    fprintf('3D Match: %s\n\n', mat2str(isequal(expected_3d, result_3d)));
    
    % Test 4: Context similar to actual usage in compute_biaxial_cao_error
    % Simulate J_fwd and R_fwd dimensions
    fprintf('Test 4 - Actual Usage Context:\n');
    
    % Create test data similar to what would be in the axis extraction
    [C0, C1] = read_surfaces('A', 1, false);
    C_small = [C0(:, 1:100), C1(:, 1:100)]; % Use small subset for testing
    
    % Get a test axis
    test_vt = [0.1; 0.9; 0.4; 10; -5; 20]; % Random axis
    
    % Compute error and Jacobian 
    [R_fwd, J_fwd] = compute_cao_error(test_vt, C_small);
    
    fprintf('J_fwd dimensions: %s\n', mat2str(size(J_fwd)));
    fprintf('R_fwd dimensions: %s\n', mat2str(size(R_fwd)));
    
    % Test the actual tmult call from compute_biaxial_cao_error line 36
    R_fwd_reshaped = reshape(R_fwd, [size(R_fwd,1), 1, size(R_fwd,2)]);
    fprintf('R_fwd_reshaped dimensions: %s\n', mat2str(size(R_fwd_reshaped)));
    
    try
        g_fwd = reshape(tmult(J_fwd, R_fwd_reshaped, 1), 6, []);
        fprintf('✓ tmult call successful, g_fwd dimensions: %s\n', mat2str(size(g_fwd)));
        
        % Check if results are reasonable (not NaN/Inf)
        nan_count = sum(isnan(g_fwd(:)));
        inf_count = sum(isinf(g_fwd(:)));
        fprintf('NaN count: %d, Inf count: %d\n', nan_count, inf_count);
        
        if nan_count == 0 && inf_count == 0
            fprintf('✓ Results are numerically stable\n');
        else
            fprintf('❌ Results contain NaN or Inf - potential mathematical error\n');
        end
        
    catch ME
        fprintf('❌ tmult call failed: %s\n', ME.message);
    end
    
    fprintf('\n=== tmult Verification Complete ===\n');
    
catch ME
    fprintf('❌ Verification failed: %s\n', ME.message);
end