% Diagnose exact MATLAB error location
addpath('/data/gpfs/projects/punim2657/sfs_preprocessing/AxisExtraction');

fprintf('🔍 MATLAB Error Diagnosis - Tracing Exact Failure Point\n\n');

try
    % Step 1: Test file reading
    fprintf('📂 Step 1: Testing file reading...\n');
    file0 = '/data/gpfs/projects/punim2657/sfs_preprocessing/Surfaces/Plt_A_Piece_01_Surface_0.xyz';
    file1 = '/data/gpfs/projects/punim2657/sfs_preprocessing/Surfaces/Plt_A_Piece_01_Surface_1.xyz';
    
    data0 = readmatrix(file0, 'FileType', 'text');
    data1 = readmatrix(file1, 'FileType', 'text');
    
    fprintf('   ✅ Raw file reading successful\n');
    fprintf('   📊 File 0: %d×%d, File 1: %d×%d\n', size(data0), size(data1));
    
    % Step 2: Test transpose
    fprintf('\n📐 Step 2: Testing transpose operations...\n');
    C0 = data0';
    C1 = data1';
    
    fprintf('   ✅ Transpose successful\n');
    fprintf('   📊 After transpose - C0: %d×%d, C1: %d×%d\n', size(C0), size(C1));
    
    % Step 3: Test size matching
    fprintf('\n⚖️  Step 3: Testing size matching...\n');
    min_points = min(size(C0, 2), size(C1, 2));
    C0_matched = C0(:, 1:min_points);
    C1_matched = C1(:, 1:min_points);
    
    fprintf('   ✅ Size matching successful\n');
    fprintf('   📊 Matched sizes - C0: %d×%d, C1: %d×%d\n', size(C0_matched), size(C1_matched));
    
    % Step 4: Test concatenation (the critical operation)
    fprintf('\n🔗 Step 4: Testing concatenation...\n');
    C_combined = [C0_matched, C1_matched];
    
    fprintf('   ✅ Concatenation successful\n');
    fprintf('   📊 Combined size: %d×%d\n', size(C_combined));
    
    % Step 5: Test the exact operation that fails
    fprintf('\n🎯 Step 5: Testing exact run_potsac call...\n');
    
    % Call the function with debug wrapper
    try
        vt = run_potsac(C0_matched(:,1:1:end), C1_matched(:,1:1:end));
        fprintf('   ✅ run_potsac successful!\n');
        fprintf('   📊 Output size: %d×%d\n', size(vt));
    catch ME_inner
        fprintf('   ❌ run_potsac failed at: %s\n', ME_inner.message);
        fprintf('   📍 Error in function: %s\n', ME_inner.stack(1).name);
        fprintf('   📍 Error at line: %d\n', ME_inner.stack(1).line);
        
        % Test with smaller subset to isolate issue
        fprintf('\n🔬 Step 5b: Testing with smaller subset...\n');
        test_size = 1000;
        
        try
            vt_small = run_potsac(C0_matched(:,1:test_size), C1_matched(:,1:test_size));
            fprintf('   ✅ Small dataset works! Issue is dataset size.\n');
            fprintf('   💡 Solution: Algorithm needs size optimization, not format fix.\n');
        catch ME_small
            fprintf('   ❌ Small dataset also fails: %s\n', ME_small.message);
            fprintf('   💡 Issue is algorithm implementation, not dataset size.\n');
        end
    end
    
catch ME
    fprintf('❌ Error in diagnostic: %s\n', ME.message);
    fprintf('📍 Error location: %s line %d\n', ME.stack(1).name, ME.stack(1).line);
end

fprintf('\n🎯 DIAGNOSIS COMPLETE\n');
exit(0);