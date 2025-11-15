function extract_single_axis(piece_num)
% Extract axis for a single piece number
% Usage: matlab -batch "extract_single_axis(1)"

if ischar(piece_num)
    piece_num = str2double(piece_num);
end

fprintf('=== EXTRACTING AXIS FOR PIECE %02d ===\n', piece_num);

% Set up paths
addpath('AxisExtraction/');
addpath('TPS_Processing_Workspace/Surfaces/');

% Create output directories
if ~exist('TPS_Output', 'dir')
    mkdir('TPS_Output');
end
if ~exist('TPS_Output/Axes', 'dir')
    mkdir('TPS_Output/Axes');
end

% Define file paths
surface_0_file = sprintf('TPS_Processing_Workspace/Surfaces/Pot_A_Piece_%02d_Surface_0.xyz', piece_num);
surface_1_file = sprintf('TPS_Processing_Workspace/Surfaces/Pot_A_Piece_%02d_Surface_1.xyz', piece_num);
axis_output_file = sprintf('TPS_Output/Axes/Pot_A_Piece_%02d_Axis.xyz', piece_num);

% Check if surface files exist
if ~exist(surface_0_file, 'file') || ~exist(surface_1_file, 'file')
    fprintf('  ❌ Surface files not found for piece %02d\n', piece_num);
    return;
end

try
    % Load surface data
    fprintf('  📁 Loading TPS surfaces...\n');
    surface_0_data = load(surface_0_file);
    surface_1_data = load(surface_1_file);
    
    fprintf('  📊 Surface 0: %d points\n', size(surface_0_data, 1));
    fprintf('  📊 Surface 1: %d points\n', size(surface_1_data, 1));
    
    % Extract points and normals
    points_0 = surface_0_data(:, 1:3);
    normals_0 = surface_0_data(:, 4:6);
    points_1 = surface_1_data(:, 1:3);
    normals_1 = surface_1_data(:, 4:6);
    
    % Combine surfaces for axis extraction
    all_points = [points_0; points_1];
    all_normals = [normals_0; normals_1];
    
    fprintf('  🔄 Running PotSAC axis extraction...\n');
    
    % PotSAC expects data in [6 x N] format
    C_data = [all_points, all_normals]';
    
    fprintf('  🔄 Data format: %dx%d\n', size(C_data, 1), size(C_data, 2));
    
    % Call the main PotSAC axis extraction function
    axis_candidates = run_potsac(C_data);
    
    if size(axis_candidates, 1) >= 6 && size(axis_candidates, 2) >= 1
        num_candidates = size(axis_candidates, 2);
        fprintf('  ✅ PotSAC extracted %d axis candidates\n', num_candidates);
        
        % Save all candidates with improved detection logic
        fid = fopen(axis_output_file, 'w');
        for cand_idx = 1:num_candidates
            % CRITICAL FIX: PotSAC returns inconsistent data structures
            rows_1_3 = axis_candidates(1:3, cand_idx);
            rows_4_6 = axis_candidates(4:6, cand_idx);
            
            norm_1_3 = norm(rows_1_3);
            norm_4_6 = norm(rows_4_6);
            
            fprintf('  🔍 Candidate %d: norm(1:3)=%.3f, norm(4:6)=%.3f\n', ...
                   cand_idx, norm_1_3, norm_4_6);
            
            % Detect which is direction (normalized) vs position (larger coordinates)
            if abs(norm_1_3 - 1.0) < 0.1
                direction = rows_1_3 / norm(rows_1_3);
                position = rows_4_6;
                fprintf('  📍 Standard format: direction=[%.3f,%.3f,%.3f], position=[%.1f,%.1f,%.1f]\n', ...
                       direction(1), direction(2), direction(3), position(1), position(2), position(3));
            elseif abs(norm_4_6 - 1.0) < 0.1
                direction = rows_4_6 / norm(rows_4_6);
                position = rows_1_3;
                fprintf('  📍 Swapped format: direction=[%.3f,%.3f,%.3f], position=[%.1f,%.1f,%.1f]\n', ...
                       direction(1), direction(2), direction(3), position(1), position(2), position(3));
            else
                fprintf('  ⚠️  Neither clearly normalized, using default: rows 1:3=direction\n');
                direction = rows_1_3 / norm(rows_1_3);
                position = rows_4_6;
            end
            
            % Write in sample format: position first, then direction
            fprintf(fid, '%.6f %.6f %.6f %.6f %.6f %.6f\n', ...
                position(1), position(2), position(3), ...
                direction(1), direction(2), direction(3));
        end
        fclose(fid);
        
        fprintf('  ✅ Successfully processed piece %02d\n', piece_num);
        
    else
        fprintf('  ❌ PotSAC returned invalid or empty axis candidates\n');
        fprintf('     Returned size: %dx%d\n', size(axis_candidates, 1), size(axis_candidates, 2));
    end
    
catch axis_error
    fprintf('  ❌ PotSAC failed with error: %s\n', axis_error.message);
    fprintf('     This requires debugging the PotSAC algorithm implementation\n');
end

fprintf('\n=== PIECE %02d AXIS EXTRACTION COMPLETE ===\n', piece_num);
end