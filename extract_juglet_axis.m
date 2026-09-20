function ok = extract_juglet_axis(surface_0_file, surface_1_file, axis_output_file)
% Extract a PotSAC symmetry axis for one Juglet sherd from its two surface
% sheets. Same core as extract_single_axis (Pot_A), but paths come from the
% caller: nothing Pot_A-specific may live here.
% Returns true if at least one candidate was written.

ok = false;
addpath('AxisExtraction/');

if ~exist(surface_0_file, 'file') || ~exist(surface_1_file, 'file')
    fprintf('  surface files missing:\n    %s\n    %s\n', surface_0_file, surface_1_file);
    return;
end

try
    surface_0_data = load(surface_0_file);
    surface_1_data = load(surface_1_file);
    fprintf('  Surface 0: %d points; Surface 1: %d points\n', size(surface_0_data, 1), size(surface_1_data, 1));

    points_0 = surface_0_data(:, 1:3);
    normals_0 = surface_0_data(:, 4:6);
    points_1 = surface_1_data(:, 1:3);
    normals_1 = surface_1_data(:, 4:6);

    all_points = [points_0; points_1];
    all_normals = [normals_0; normals_1];

    % PotSAC expects data in [6 x N] format
    C_data = [all_points, all_normals]';

    axis_candidates = run_potsac(C_data);

    if size(axis_candidates, 1) >= 6 && size(axis_candidates, 2) >= 1
        num_candidates = size(axis_candidates, 2);
        fprintf('  PotSAC extracted %d axis candidates\n', num_candidates);

        fid = fopen(axis_output_file, 'w');
        for cand_idx = 1:num_candidates
            rows_1_3 = axis_candidates(1:3, cand_idx);
            rows_4_6 = axis_candidates(4:6, cand_idx);

            norm_1_3 = norm(rows_1_3);
            norm_4_6 = norm(rows_4_6);

            % Detect which is direction (normalized) vs position (larger coordinates)
            if abs(norm_1_3 - 1.0) < 0.1
                direction = rows_1_3 / norm(rows_1_3);
                position = rows_4_6;
            elseif abs(norm_4_6 - 1.0) < 0.1
                direction = rows_4_6 / norm(rows_4_6);
                position = rows_1_3;
            else
                fprintf('  neither half normalized, using rows 1:3=direction\n');
                direction = rows_1_3 / norm(rows_1_3);
                position = rows_4_6;
            end

            % Write in sample format: position first, then direction
            fprintf(fid, '%.6f %.6f %.6f %.6f %.6f %.6f\n', ...
                position(1), position(2), position(3), ...
                direction(1), direction(2), direction(3));
        end
        fclose(fid);
        ok = true;
    else
        fprintf('  PotSAC returned invalid or empty axis candidates\n');
    end
catch axis_error
    fprintf('  PotSAC failed with error: %s\n', axis_error.message);
end
end
