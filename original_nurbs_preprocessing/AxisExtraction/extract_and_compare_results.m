% Extract and compare NURBS axis results with sample data
fprintf('=== NURBS AXIS RESULTS EXTRACTION ===\n');

% Extract piece 1
[vt1] = extract_axis_nurbs('A', 1);
fprintf('\nPiece 01 Results:\n');
if ~isempty(vt1)
    % Take the best axis result (first one)
    direction = vt1(1:3, 1);
    position = vt1(4:6, 1);
    fprintf('Direction: [%.3f, %.3f, %.3f]\n', direction(1), direction(2), direction(3));
    fprintf('Position: [%.3f, %.3f, %.3f]\n', position(1), position(2), position(3));
    
    % Save in sample format
    axis_file = 'Pot_A_Piece_01_NURBS_Axis.xyz';
    fid = fopen(axis_file, 'w');
    fprintf(fid, '%.12f %.12f %.12f %.12f %.12f %.12f\n', position(1), position(2), position(3), direction(1), direction(2), direction(3));
    fclose(fid);
    fprintf('Saved to: %s\n', axis_file);
else
    fprintf('No axis found for piece 01\n');
end

% Extract piece 2
[vt2] = extract_axis_nurbs('A', 2);
fprintf('\nPiece 02 Results:\n');
if ~isempty(vt2)
    direction = vt2(1:3, 1);
    position = vt2(4:6, 1);
    fprintf('Direction: [%.3f, %.3f, %.3f]\n', direction(1), direction(2), direction(3));
    fprintf('Position: [%.3f, %.3f, %.3f]\n', position(1), position(2), position(3));
    
    axis_file = 'Pot_A_Piece_02_NURBS_Axis.xyz';
    fid = fopen(axis_file, 'w');
    fprintf(fid, '%.12f %.12f %.12f %.12f %.12f %.12f\n', position(1), position(2), position(3), direction(1), direction(2), direction(3));
    fclose(fid);
    fprintf('Saved to: %s\n', axis_file);
else
    fprintf('No axis found for piece 02\n');
end

fprintf('\n=== COMPARISON WITH SAMPLE DATA ===\n');

% Load and display sample data
sample_1 = load('/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp/Axes/Pot_A_Piece_01_Axis.xyz');
sample_2 = load('/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp/Axes/Pot_A_Piece_02_Axis.xyz');

fprintf('\nSample Piece 01:\n');
fprintf('Position: [%.3f, %.3f, %.3f]\n', sample_1(1), sample_1(2), sample_1(3));
fprintf('Direction: [%.3f, %.3f, %.3f]\n', sample_1(4), sample_1(5), sample_1(6));

fprintf('\nSample Piece 02:\n');
fprintf('Position: [%.3f, %.3f, %.3f]\n', sample_2(1), sample_2(2), sample_2(3));
fprintf('Direction: [%.3f, %.3f, %.3f]\n', sample_2(4), sample_2(5), sample_2(6));

% Calculate differences
if ~isempty(vt1)
    pos_diff_1 = norm([position(1), position(2), position(3)] - [sample_1(1), sample_1(2), sample_1(3)]);
    dir_diff_1 = norm([direction(1), direction(2), direction(3)] - [sample_1(4), sample_1(5), sample_1(6)]);
    fprintf('\nPiece 01 Differences:\n');
    fprintf('Position difference: %.3f units\n', pos_diff_1);
    fprintf('Direction difference: %.3f units\n', dir_diff_1);
end

if ~isempty(vt2)
    vt2_direction = vt2(1:3, 1);
    vt2_position = vt2(4:6, 1);
    pos_diff_2 = norm([vt2_position(1), vt2_position(2), vt2_position(3)] - [sample_2(1), sample_2(2), sample_2(3)]);
    dir_diff_2 = norm([vt2_direction(1), vt2_direction(2), vt2_direction(3)] - [sample_2(4), sample_2(5), sample_2(6)]);
    fprintf('\nPiece 02 Differences:\n');
    fprintf('Position difference: %.3f units\n', pos_diff_2);
    fprintf('Direction difference: %.3f units\n', dir_diff_2);
end