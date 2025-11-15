% Debug script to check PotSAC output structure
addpath('AxisExtraction/');
fprintf('=== DEBUGGING POTSAC OUTPUT ===\n');

% Load one test surface
surface_0_file = 'TPS_Processing_Workspace/Surfaces/Pot_A_Piece_01_Surface_0.xyz';
surface_1_file = 'TPS_Processing_Workspace/Surfaces/Pot_A_Piece_01_Surface_1.xyz';

surface_0_data = load(surface_0_file);
surface_1_data = load(surface_1_file);

points_0 = surface_0_data(:, 1:3);
normals_0 = surface_0_data(:, 4:6);
points_1 = surface_1_data(:, 1:3);
normals_1 = surface_1_data(:, 4:6);

all_points = [points_0; points_1];
all_normals = [normals_0; normals_1];
C_data = [all_points, all_normals]';

fprintf('Input data size: %dx%d\n', size(C_data, 1), size(C_data, 2));

% Call PotSAC
axis_candidates = run_potsac(C_data);

fprintf('Output size: %dx%d\n', size(axis_candidates, 1), size(axis_candidates, 2));
fprintf('First candidate raw values:\n');
for i = 1:6
    fprintf('  Row %d: %.6f\n', i, axis_candidates(i, 1));
end

fprintf('\nAnalysis:\n');
fprintf('  Rows 1-3: [%.6f, %.6f, %.6f] (norm=%.6f)\n', axis_candidates(1:3, 1), norm(axis_candidates(1:3, 1)));
fprintf('  Rows 4-6: [%.6f, %.6f, %.6f] (norm=%.6f)\n', axis_candidates(4:6, 1), norm(axis_candidates(4:6, 1)));

% Check if rows 1-3 are normalized (direction) or rows 4-6 are normalized
if abs(norm(axis_candidates(1:3, 1)) - 1.0) < 0.01
    fprintf('  → Rows 1-3 appear to be NORMALIZED DIRECTION\n');
    fprintf('  → Rows 4-6 appear to be POSITION\n');
elseif abs(norm(axis_candidates(4:6, 1)) - 1.0) < 0.01
    fprintf('  → Rows 4-6 appear to be NORMALIZED DIRECTION\n');
    fprintf('  → Rows 1-3 appear to be POSITION\n');
else
    fprintf('  → Neither set is clearly normalized - check structure\n');
end