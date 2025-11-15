fprintf('=== DEBUGGING PIECE 02 AXIS EXTRACTION ===\n');
addpath('AxisExtraction/');

% Load Piece 02 surfaces
surface_0_file = 'TPS_Processing_Workspace/Surfaces/Pot_A_Piece_02_Surface_0.xyz';
surface_1_file = 'TPS_Processing_Workspace/Surfaces/Pot_A_Piece_02_Surface_1.xyz';

surface_0_data = load(surface_0_file);
surface_1_data = load(surface_1_file);

points_0 = surface_0_data(:, 1:3);
normals_0 = surface_0_data(:, 4:6);
points_1 = surface_1_data(:, 1:3);
normals_1 = surface_1_data(:, 4:6);

all_points = [points_0; points_1];
all_normals = [normals_0; normals_1];
C_data = [all_points, all_normals]';

fprintf('Piece 02 input data size: %dx%d\n', size(C_data, 1), size(C_data, 2));

% Call PotSAC
axis_candidates = run_potsac(C_data);

fprintf('PotSAC output size: %dx%d\n', size(axis_candidates, 1), size(axis_candidates, 2));
fprintf('Raw PotSAC values for first candidate:\n');
for i = 1:6
    fprintf('  Row %d: %.6f\n', i, axis_candidates(i, 1));
end

% Analyze which is direction vs position
rows_1_3 = axis_candidates(1:3, 1);
rows_4_6 = axis_candidates(4:6, 1);
norm_1_3 = norm(rows_1_3);
norm_4_6 = norm(rows_4_6);

fprintf('\nAnalysis:\n');
fprintf('Rows 1-3: [%.6f, %.6f, %.6f] (norm=%.6f)\n', rows_1_3(1), rows_1_3(2), rows_1_3(3), norm_1_3);
fprintf('Rows 4-6: [%.6f, %.6f, %.6f] (norm=%.6f)\n', rows_4_6(1), rows_4_6(2), rows_4_6(3), norm_4_6);

if abs(norm_1_3 - 1.0) < 0.1
    fprintf('→ Rows 1-3 appear to be DIRECTION (normalized)\n');
    fprintf('→ Rows 4-6 appear to be POSITION\n');
    direction = rows_1_3 / norm(rows_1_3);
    position = rows_4_6;
elseif abs(norm_4_6 - 1.0) < 0.1
    fprintf('→ Rows 4-6 appear to be DIRECTION (normalized)\n');
    fprintf('→ Rows 1-3 appear to be POSITION\n');
    direction = rows_4_6 / norm(rows_4_6);
    position = rows_1_3;
else
    fprintf('→ Neither set is clearly normalized, using default assignment\n');
    direction = rows_1_3 / norm(rows_1_3);
    position = rows_4_6;
end

fprintf('\nFinal assignment:\n');
fprintf('Direction: [%.6f, %.6f, %.6f]\n', direction(1), direction(2), direction(3));
fprintf('Position:  [%.6f, %.6f, %.6f]\n', position(1), position(2), position(3));

% Write in sample format (position first, then direction)
result_line = sprintf('%.6f %.6f %.6f %.6f %.6f %.6f', position(1), position(2), position(3), direction(1), direction(2), direction(3));
fprintf('\nResult: %s\n', result_line);
