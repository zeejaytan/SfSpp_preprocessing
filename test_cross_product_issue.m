% Test the exact cross product issue
addpath('/data/gpfs/projects/punim2657/sfs_preprocessing/AxisExtraction');

fprintf('🔍 Testing exact cross product issue...\n\n');

% Simulate the problematic input that causes the cross product to fail
fprintf('📊 Creating test data that replicates the error...\n');

% Create a 6×6 matrix (which is what gets passed to euc2plucker)
test_data = rand(6, 6);
fprintf('   Test data size: %d×%d\n', size(test_data));

% Test the cross product operation that fails
try
    fprintf('🧮 Testing cross(test_data(4:6,:), test_data(1:3,:))...\n');
    result = cross(test_data(4:6,:), test_data(1:3,:));
    fprintf('   ✅ Cross product successful: %d×%d\n', size(result));
catch ME
    fprintf('   ❌ Cross product failed: %s\n', ME.message);
end

% Test with different dimensions to understand the issue
fprintf('\n🔬 Testing different input dimensions...\n');

for cols = [1, 3, 6, 10]
    test_matrix = rand(6, cols);
    try
        result = cross(test_matrix(4:6,:), test_matrix(1:3,:));
        fprintf('   ✅ Size %d×%d: SUCCESS\n', 6, cols);
    catch ME
        fprintf('   ❌ Size %d×%d: FAILED - %s\n', 6, cols, ME.message);
    end
end

% Test the actual issue by checking MATLAB cross function requirements
fprintf('\n📚 MATLAB cross function requirements:\n');
fprintf('   cross(A,B) requires A and B to have the same size\n');
fprintf('   OR one of them must be a 3×1 or 1×3 vector\n');

% Let me check what our actual data looks like
fprintf('\n🔍 Checking our actual surface data...\n');
try
    [C0, C1] = read_surfaces('A', 1, false);
    fprintf('   Surface data loaded: C0=%d×%d, C1=%d×%d\n', size(C0), size(C1));
    
    % Test with actual data
    C_combined = [C0, C1];
    fprintf('   Combined data: %d×%d\n', size(C_combined));
    
    % Simulate what happens in the algorithm
    num_points = size(C_combined, 2);
    sample_size = 6;
    sample_indices = randsample(num_points, sample_size);
    C_sample = C_combined(:, sample_indices);
    fprintf('   Sample data: %d×%d\n', size(C_sample));
    
    % This is what gets passed to euc2plucker
    fprintf('   Testing euc2plucker with sample...\n');
    X = C_sample([4:6,1:3],:);  % Reorder as expected by euc2plucker
    fprintf('   Input to euc2plucker: %d×%d\n', size(X));
    
    % Test the actual cross product that fails
    try
        result = cross(X(4:6,:), X(1:3,:));
        fprintf('   ✅ Cross product with real data: SUCCESS\n');
    catch ME
        fprintf('   ❌ Cross product with real data: FAILED - %s\n', ME.message);
        
        % Debug the exact dimensions
        part1 = X(4:6,:);
        part2 = X(1:3,:);
        fprintf('   🔍 part1 (X(4:6,:)): %d×%d\n', size(part1));
        fprintf('   🔍 part2 (X(1:3,:)): %d×%d\n', size(part2));
    end
    
catch ME
    fprintf('   ❌ Failed to load surface data: %s\n', ME.message);
end

fprintf('\n🎯 Cross product diagnosis complete.\n');
exit(0);