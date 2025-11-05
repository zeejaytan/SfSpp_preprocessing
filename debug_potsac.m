function debug_potsac()
% Debug version to find where PotSAC fails with NURBS data
% Test with smaller data sizes to isolate the issue

fprintf('=== DEBUGGING POTSAC WITH NURBS DATA ===\n');

% Load NURBS surface data
surface_0_file = '../Temp/Data/Pot_A/Pot_A_Piece_01_Surface_0.xyz';
surface_1_file = '../Temp/Data/Pot_A/Pot_A_Piece_01_Surface_1.xyz';

if ~exist(surface_0_file, 'file') || ~exist(surface_1_file, 'file')
    fprintf('❌ NURBS surface files not found\n');
    return;
end

try
    % Load surfaces
    surface_0_data = load(surface_0_file);
    surface_1_data = load(surface_1_file);
    
    fprintf('📊 NURBS Surface 0: %d points\n', size(surface_0_data, 1));
    fprintf('📊 NURBS Surface 1: %d points\n', size(surface_1_data, 1));
    
    % Test with different subsampling rates to isolate size dependency
    test_rates = [100, 50, 20, 10, 5]; % Sample every N points
    
    for rate = test_rates
        fprintf('\n🔄 Testing with subsampling rate 1:%d\n', rate);
        
        % Subsample surfaces
        C0_sub = surface_0_data(1:rate:end, :)';  % [6 x N]
        C1_sub = surface_1_data(1:rate:end, :)';  % [6 x N]
        
        fprintf('   Subsampled Surface 0: %dx%d\n', size(C0_sub, 1), size(C0_sub, 2));
        fprintf('   Subsampled Surface 1: %dx%d\n', size(C1_sub, 1), size(C1_sub, 2));
        
        try
            % Try PotSAC with subsampled data
            addpath('AxisExtraction/');
            axis_candidates = run_potsac(C0_sub, C1_sub);
            
            fprintf('   ✅ SUCCESS! PotSAC worked with %d points\n', size(C0_sub, 2) + size(C1_sub, 2));
            fprintf('   📍 Extracted %d axis candidates\n', size(axis_candidates, 2));
            
            % Test successful - show first candidate
            if size(axis_candidates, 2) >= 1
                rows_1_3 = axis_candidates(1:3, 1);
                rows_4_6 = axis_candidates(4:6, 1);
                
                norm_1_3 = norm(rows_1_3);
                norm_4_6 = norm(rows_4_6);
                
                fprintf('   🎯 First candidate: norm(1:3)=%.3f, norm(4:6)=%.3f\n', norm_1_3, norm_4_6);
            end
            break; % Success found, exit loop
            
        catch subsample_error
            fprintf('   ❌ FAILED with %d total points: %s\n', ...
                   size(C0_sub, 2) + size(C1_sub, 2), subsample_error.message);
        end
    end
    
    % Compare with TPS data sizes for reference
    fprintf('\n📊 For comparison, TPS Surface sizes:\n');
    tps_0_file = '../../TPS_Processing_Workspace/Surfaces/Pot_A_Piece_01_Surface_0.xyz';
    tps_1_file = '../../TPS_Processing_Workspace/Surfaces/Pot_A_Piece_01_Surface_1.xyz';
    
    if exist(tps_0_file, 'file') && exist(tps_1_file, 'file')
        tps_0_data = load(tps_0_file);
        tps_1_data = load(tps_1_file);
        fprintf('   TPS Surface 0: %d points\n', size(tps_0_data, 1));
        fprintf('   TPS Surface 1: %d points\n', size(tps_1_data, 1));
        fprintf('   Total TPS points: %d\n', size(tps_0_data, 1) + size(tps_1_data, 1));
    end
    
catch debug_error
    fprintf('❌ Debug failed: %s\n', debug_error.message);
end

fprintf('\n=== POTSAC DEBUG COMPLETE ===\n');
end