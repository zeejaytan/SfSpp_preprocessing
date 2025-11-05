function extract_nurbs_axis(piece_num)
% Extract axis for a single NURBS-preprocessed piece
% Usage: matlab -batch "extract_nurbs_axis(1)"

if ischar(piece_num)
    piece_num = str2double(piece_num);
end

fprintf('=== EXTRACTING NURBS AXIS FOR PIECE %02d ===\n', piece_num);

% Set up paths for NURBS preprocessing
addpath('AxisExtraction/');

% Create output directories
if ~exist('NURBS_Output', 'dir')
    mkdir('NURBS_Output');
end
if ~exist('NURBS_Output/Axes', 'dir')
    mkdir('NURBS_Output/Axes');
end

% Define file paths for NURBS-generated surfaces
surface_0_file = sprintf('../Surfaces/Pot_A_Piece_%02d_Surface_0.xyz', piece_num);
surface_1_file = sprintf('../Surfaces/Pot_A_Piece_%02d_Surface_1.xyz', piece_num);
axis_output_file = sprintf('NURBS_Output/Axes/Pot_A_Piece_%02d_Axis.xyz', piece_num);

% Check if NURBS surface files exist
if ~exist(surface_0_file, 'file') || ~exist(surface_1_file, 'file')
    fprintf('  ❌ NURBS surface files not found for piece %02d\n', piece_num);
    fprintf('     Expected: %s\n', surface_0_file);
    fprintf('     Expected: %s\n', surface_1_file);
    return;
end

try
    % Load NURBS surface data (X Y Z Nx Ny Nz format)
    fprintf('  📁 Loading NURBS surfaces...\n');
    surface_0_data = load(surface_0_file);
    surface_1_data = load(surface_1_file);
    
    fprintf('  📊 NURBS Surface 0: %d points\n', size(surface_0_data, 1));
    fprintf('  📊 NURBS Surface 1: %d points\n', size(surface_1_data, 1));
    
    % Extract points and normals from NURBS surfaces
    points_0 = surface_0_data(:, 1:3);
    normals_0 = surface_0_data(:, 4:6);
    points_1 = surface_1_data(:, 1:3);
    normals_1 = surface_1_data(:, 4:6);
    
    % Combine surfaces for axis extraction (like working TPS version)
    all_points = [points_0; points_1];
    all_normals = [normals_0; normals_1];
    
    fprintf('  🔄 Running PotSAC on combined NURBS surfaces...\n');
    
    % PotSAC expects data in [6 x N] format (using working TPS approach)
    C_data = [all_points, all_normals]';
    
    fprintf('  🔄 Combined NURBS data format: %dx%d\n', size(C_data, 1), size(C_data, 2));
    
    % Call PotSAC with single combined array (like working TPS version)
    axis_candidates = run_potsac(C_data);
    
    if size(axis_candidates, 1) >= 6 && size(axis_candidates, 2) >= 1
        num_candidates = size(axis_candidates, 2);
        fprintf('  ✅ PotSAC extracted %d axis candidates from NURBS surfaces\n', num_candidates);
        
        % Save axis candidates with improved detection
        fid = fopen(axis_output_file, 'w');
        for cand_idx = 1:num_candidates
            % Handle PotSAC return format inconsistency
            rows_1_3 = axis_candidates(1:3, cand_idx);
            rows_4_6 = axis_candidates(4:6, cand_idx);
            
            norm_1_3 = norm(rows_1_3);
            norm_4_6 = norm(rows_4_6);
            
            fprintf('  🔍 NURBS Candidate %d: norm(1:3)=%.3f, norm(4:6)=%.3f\n', ...
                   cand_idx, norm_1_3, norm_4_6);
            
            % Detect direction (normalized) vs position (coordinates)
            if abs(norm_1_3 - 1.0) < 0.1
                direction = rows_1_3 / norm(rows_1_3);
                position = rows_4_6;
                fprintf('  📍 NURBS axis: direction=[%.3f,%.3f,%.3f], position=[%.1f,%.1f,%.1f]\n', ...
                       direction(1), direction(2), direction(3), position(1), position(2), position(3));
            elseif abs(norm_4_6 - 1.0) < 0.1
                direction = rows_4_6 / norm(rows_4_6);
                position = rows_1_3;
                fprintf('  📍 NURBS axis (swapped): direction=[%.3f,%.3f,%.3f], position=[%.1f,%.1f,%.1f]\n', ...
                       direction(1), direction(2), direction(3), position(1), position(2), position(3));
            else
                fprintf('  ⚠️  Neither clearly normalized, using default for NURBS\n');
                direction = rows_1_3 / norm(rows_1_3);
                position = rows_4_6;
            end
            
            % Write in SFS-compatible format: position first, then direction
            fprintf(fid, '%.6f %.6f %.6f %.6f %.6f %.6f\n', ...
                position(1), position(2), position(3), ...
                direction(1), direction(2), direction(3));
        end
        fclose(fid);
        
        fprintf('  ✅ Successfully processed NURBS piece %02d\n', piece_num);
        
    else
        fprintf('  ❌ PotSAC returned invalid axis candidates from NURBS data\n');
        fprintf('     Returned size: %dx%d\n', size(axis_candidates, 1), size(axis_candidates, 2));
    end
    
catch axis_error
    fprintf('  ❌ NURBS PotSAC failed with error: %s\n', axis_error.message);
    fprintf('     Check NURBS surface quality and PotSAC algorithm parameters\n');
end

fprintf('\n=== NURBS PIECE %02d AXIS EXTRACTION COMPLETE ===\n', piece_num);
end