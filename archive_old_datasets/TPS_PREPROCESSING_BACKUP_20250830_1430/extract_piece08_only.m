% Extract axis for Piece 08 only
fprintf('=== EXTRACTING AXIS FOR PIECE 08 ONLY ===\n');

% Set up paths
addpath('AxisExtraction/');
addpath('TPS_Processing_Workspace/Surfaces/');

piece_num = 8;
fprintf('\n--- Processing Pot A Piece %02d ---\n', piece_num);

% Define file paths
surface_0_file = sprintf('TPS_Processing_Workspace/Surfaces/Pot_A_Piece_%02d_Surface_0.xyz', piece_num);
surface_1_file = sprintf('TPS_Processing_Workspace/Surfaces/Pot_A_Piece_%02d_Surface_1.xyz', piece_num);
axis_output_file = sprintf('TPS_Output/Axes/Pot_A_Piece_%02d_Axis.xyz', piece_num);

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
        
        % Save all candidates with detection logic
        fid = fopen(axis_output_file, 'w');
        for cand_idx = 1:num_candidates
            rows_1_3 = axis_candidates(1:3, cand_idx);
            rows_4_6 = axis_candidates(4:6, cand_idx);
            
            norm_1_3 = norm(rows_1_3);
            norm_4_6 = norm(rows_4_6);
            
            % Detect which is direction vs position
            if abs(norm_1_3 - 1.0) < 0.1
                direction = rows_1_3 / norm(rows_1_3);
                position = rows_4_6;
            elseif abs(norm_4_6 - 1.0) < 0.1
                direction = rows_4_6 / norm(rows_4_6);
                position = rows_1_3;
            else
                direction = rows_1_3 / norm(rows_1_3);
                position = rows_4_6;
            end
            
            % Write: position first, then direction
            fprintf(fid, '%.6f %.6f %.6f %.6f %.6f %.6f\n', ...
                position(1), position(2), position(3), ...
                direction(1), direction(2), direction(3));
        end
        fclose(fid);
        
        fprintf('  ✅ Successfully processed piece %02d\n', piece_num);
    end
    
catch error
    fprintf('  ❌ Error: %s\n', error.message);
end

fprintf('\n=== PIECE 08 COMPLETE ===\n');