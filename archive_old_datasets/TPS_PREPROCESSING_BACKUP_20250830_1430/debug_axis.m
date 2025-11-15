% Debug axis extraction
addpath('/data/gpfs/projects/punim2657/sfs_preprocessing/AxisExtraction');

try
    fprintf('🔍 Starting debug of axis extraction\n');
    
    % Test reading surface files
    [C0, C1] = read_surfaces('A', 1, false);
    
    fprintf('📊 Surface data dimensions:\n');
    fprintf('   C0 size: %d × %d\n', size(C0, 1), size(C0, 2));
    fprintf('   C1 size: %d × %d\n', size(C1, 1), size(C1, 2));
    
    % Check if dimensions match
    if size(C0, 1) ~= size(C1, 1) || size(C0, 2) ~= size(C1, 2)
        fprintf('❌ Size mismatch detected!\n');
        fprintf('   C0: %d×%d vs C1: %d×%d\n', size(C0), size(C1));
    else
        fprintf('✅ Surface dimensions match\n');
    end
    
    % Try to run potsac with debug info
    fprintf('🔄 Testing potsac function...\n');
    fprintf('   Input sizes - C0: %d×%d, C1: %d×%d\n', size(C0), size(C1));
    
    % Test concatenation (what potsac does internally)
    try
        C_combined = [C0, C1];
        fprintf('   ✅ Concatenation successful: %d×%d\n', size(C_combined));
    catch ME2
        fprintf('   ❌ Concatenation failed: %s\n', ME2.message);
    end
    
    vt = run_potsac(C0(:,1:1:end), C1(:,1:1:end));
    fprintf('✅ Potsac succeeded, output size: %d×%d\n', size(vt));
    
catch ME
    fprintf('❌ Error: %s\n', ME.message);
    if contains(ME.message, 'same size')
        fprintf('🔍 Investigating size mismatch...\n');
        
        % Check file existence and basic properties
        file0 = '/data/gpfs/projects/punim2657/sfs_preprocessing/Surfaces/Plt_A_Piece_01_Surface_0.xyz';
        file1 = '/data/gpfs/projects/punim2657/sfs_preprocessing/Surfaces/Plt_A_Piece_01_Surface_1.xyz';
        
        if exist(file0, 'file')
            data0 = readmatrix(file0);
            fprintf('   File 0 raw size: %d×%d\n', size(data0));
        end
        
        if exist(file1, 'file')
            data1 = readmatrix(file1);
            fprintf('   File 1 raw size: %d×%d\n', size(data1));
        end
    end
end

exit(0);