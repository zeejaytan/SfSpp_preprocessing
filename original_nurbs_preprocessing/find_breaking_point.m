function find_breaking_point()
% Find the exact sample size where NURBS PotSAC starts failing

fprintf('=== FINDING NURBS POTSAC BREAKING POINT ===\n');

% NURBS surface file
nurbs_0_file = 'Temp/Data/Pot_A/Pot_A_Piece_01_Surface_0.xyz';
nurbs_1_file = 'Temp/Data/Pot_A/Pot_A_Piece_01_Surface_1.xyz';

if ~exist(nurbs_0_file, 'file') || ~exist(nurbs_1_file, 'file')
    fprintf('❌ NURBS surface files not found\n');
    return;
end

% Load data
nurbs_0_data = load(nurbs_0_file);
nurbs_1_data = load(nurbs_1_file);

fprintf('Total NURBS points: Surface_0=%d, Surface_1=%d\n', ...
        size(nurbs_0_data, 1), size(nurbs_1_data, 1));

% Test with different sample sizes
test_sizes = [100, 200, 500, 1000, 2000, 3000, 5000, 7000, 10000, 15000, 20000];

addpath('AxisExtraction/');

for sample_size = test_sizes
    if sample_size > min(size(nurbs_0_data, 1), size(nurbs_1_data, 1))
        fprintf('⏭️  Skipping %d (exceeds available data)\n', sample_size);
        continue;
    end
    
    fprintf('🔄 Testing with %d points per surface...\n', sample_size);
    
    try
        % Sample data
        C0 = nurbs_0_data(1:sample_size, :)';  % [6 x N]
        C1 = nurbs_1_data(1:sample_size, :)';  % [6 x N]
        
        % Call PotSAC
        tic;
        axis_candidates = run_potsac(C0, C1);
        elapsed_time = toc;
        
        fprintf('   ✅ SUCCESS with %d points (%.2fs)\n', sample_size, elapsed_time);
        fprintf('   📍 Extracted %d axis candidates\n', size(axis_candidates, 2));
        
    catch sample_error
        fprintf('   ❌ FAILED with %d points: %s\n', sample_size, sample_error.message);
        
        % Found the breaking point, let's narrow it down
        if sample_size > 100
            fprintf('\n🎯 Breaking point found! Narrowing down between %d and %d...\n', ...
                   test_sizes(find(test_sizes == sample_size) - 1), sample_size);
            
            prev_working = test_sizes(find(test_sizes == sample_size) - 1);
            narrow_range = prev_working:100:sample_size;
            
            for narrow_size = narrow_range
                if narrow_size > min(size(nurbs_0_data, 1), size(nurbs_1_data, 1))
                    break;
                end
                
                fprintf('   🔍 Testing %d points...\n', narrow_size);
                
                try
                    C0_narrow = nurbs_0_data(1:narrow_size, :)';
                    C1_narrow = nurbs_1_data(1:narrow_size, :)';
                    
                    axis_candidates = run_potsac(C0_narrow, C1_narrow);
                    fprintf('      ✅ %d points: SUCCESS\n', narrow_size);
                    
                catch narrow_error
                    fprintf('      ❌ %d points: FAILED (%s)\n', narrow_size, narrow_error.message);
                    fprintf('\n🎯 EXACT BREAKING POINT: Between %d and %d points\n', ...
                           narrow_size - 100, narrow_size);
                    break;
                end
            end
        end
        break; % Exit main loop after finding breaking point
    end
end

% Compare with TPS successful case
fprintf('\n=== COMPARISON WITH TPS ===\n');
tps_0_file = '../TPS_Processing_Workspace/Surfaces/Pot_A_Piece_01_Surface_0.xyz';
tps_1_file = '../TPS_Processing_Workspace/Surfaces/Pot_A_Piece_01_Surface_1.xyz';

if exist(tps_0_file, 'file') && exist(tps_1_file, 'file')
    tps_0_data = load(tps_0_file);
    tps_1_data = load(tps_1_file);
    
    fprintf('TPS total points: Surface_0=%d, Surface_1=%d\n', ...
           size(tps_0_data, 1), size(tps_1_data, 1));
    
    try
        fprintf('Testing TPS with full dataset...\n');
        C0_tps = tps_0_data';
        C1_tps = tps_1_data';
        
        tic;
        axis_candidates_tps = run_potsac(C0_tps, C1_tps);
        tps_time = toc;
        
        fprintf('✅ TPS SUCCESS with full dataset (%.2fs)\n', tps_time);
        fprintf('📍 TPS extracted %d axis candidates\n', size(axis_candidates_tps, 2));
        
    catch tps_error
        fprintf('❌ TPS also failed: %s\n', tps_error.message);
    end
end

fprintf('\n=== BREAKING POINT ANALYSIS COMPLETE ===\n');
end