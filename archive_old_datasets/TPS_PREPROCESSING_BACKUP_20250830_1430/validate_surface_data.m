% Validate TPS surface data quality for axis extraction
addpath('/data/gpfs/projects/punim2657/sfs_preprocessing/AxisExtraction');

fprintf('🔍 Validating TPS surface data quality...\n');

% Read raw surface files
file0 = '/data/gpfs/projects/punim2657/sfs_preprocessing/Surfaces/Plt_A_Piece_01_Surface_0.xyz';
file1 = '/data/gpfs/projects/punim2657/sfs_preprocessing/Surfaces/Plt_A_Piece_01_Surface_1.xyz';

data0 = readmatrix(file0, 'FileType', 'text');
data1 = readmatrix(file1, 'FileType', 'text');

fprintf('📊 Raw data dimensions:\n');
fprintf('   Surface 0: %d × %d\n', size(data0));
fprintf('   Surface 1: %d × %d\n', size(data1));

% Check for invalid values
fprintf('🔍 Checking for invalid values...\n');

% Check Surface 0
nan_count_0 = sum(isnan(data0(:)));
inf_count_0 = sum(isinf(data0(:)));
fprintf('   Surface 0 - NaN: %d, Inf: %d\n', nan_count_0, inf_count_0);

% Check Surface 1  
nan_count_1 = sum(isnan(data1(:)));
inf_count_1 = sum(isinf(data1(:)));
fprintf('   Surface 1 - NaN: %d, Inf: %d\n', nan_count_1, inf_count_1);

% Check normal vector magnitudes
fprintf('🔍 Checking normal vector quality...\n');
normals0 = data0(:, 4:6);
normals1 = data1(:, 4:6);

norm_mag_0 = sqrt(sum(normals0.^2, 2));
norm_mag_1 = sqrt(sum(normals1.^2, 2));

fprintf('   Surface 0 normal magnitudes - min: %.6f, max: %.6f, mean: %.6f\n', ...
        min(norm_mag_0), max(norm_mag_0), mean(norm_mag_0));
fprintf('   Surface 1 normal magnitudes - min: %.6f, max: %.6f, mean: %.6f\n', ...
        min(norm_mag_1), max(norm_mag_1), mean(norm_mag_1));

% Check for zero normals
zero_normals_0 = sum(norm_mag_0 < 1e-10);
zero_normals_1 = sum(norm_mag_1 < 1e-10);
fprintf('   Zero/tiny normals - Surface 0: %d, Surface 1: %d\n', zero_normals_0, zero_normals_1);

% Test the exact operations that axis extraction does
fprintf('🔍 Testing axis extraction operations...\n');

try
    % Read using the actual axis extraction function
    [C0, C1] = read_surfaces('A', 1, false);
    fprintf('   ✅ read_surfaces completed successfully\n');
    fprintf('   📐 Resampled dimensions: C0=%d×%d, C1=%d×%d\n', size(C0), size(C1));
    
    % Test concatenation
    C_combined = [C0, C1];
    fprintf('   ✅ Concatenation successful: %d×%d\n', size(C_combined));
    
    % Test normalization (what compute_axis_of_symmetry does first)
    C_test = C_combined;
    C_test(4:6,:) = C_test(4:6,:) ./ sqrt(sum(C_test(4:6,:).^2));
    fprintf('   ✅ Normal normalization successful\n');
    
    % Test random sampling (what RANSAC does)
    num_points = size(C_test, 2);
    sample_size = 6;
    kidx = randsample(num_points, sample_size);
    Cs = C_test(:, kidx);
    fprintf('   ✅ Random sampling successful: %d×%d sample\n', size(Cs));
    
    % Test the cross product operations
    test_cross = cross(Cs(4:6,:), Cs(1:3,:));
    fprintf('   ✅ Cross product test successful: %d×%d result\n', size(test_cross));
    
    % Check for any NaN or Inf in intermediate results
    if any(isnan(test_cross(:))) || any(isinf(test_cross(:)))
        fprintf('   ❌ Cross product produced invalid values!\n');
    else
        fprintf('   ✅ Cross product results are valid\n');
    end
    
catch ME
    fprintf('   ❌ Error in axis extraction operations: %s\n', ME.message);
    fprintf('   📍 Error location: %s\n', ME.stack(1).name);
end

fprintf('\n🎯 Summary: ');
if (nan_count_0 + inf_count_0 + nan_count_1 + inf_count_1) == 0
    fprintf('Surface data appears clean and valid for axis extraction\n');
else
    fprintf('Surface data has invalid values that need fixing\n');
end

exit(0);