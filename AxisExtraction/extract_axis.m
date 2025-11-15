function vt = extract_axis(pot_id, frag_id, extended)

if nargin < 3, extended = false;
end

[C0, C1] = read_surfaces(pot_id, frag_id, extended);

vt = run_potsac(C0(:,1:1:end), C1(:,1:1:end));

% Save in SFS-compatible format: single line, .xyz extension, [pos dir] order
if size(vt, 2) >= 1
    axis_dir = vt(1:3, 1);  % Direction vector
    axis_pos = vt(4:6, 1);  % Position vector
    
    % Create output directory if needed
    axis_dir_path = '../axis_output';
    if ~exist(axis_dir_path, 'dir')
        mkdir(axis_dir_path);
    end
    
    % SFS format: single line with [pos_x pos_y pos_z dir_x dir_y dir_z]
    axis_file = sprintf('../axis_output/Pot_%s_Piece_%02d_Axis.xyz', pot_id, frag_id);
    fid = fopen(axis_file, 'w');
    fprintf(fid, '%.12f %.12f %.12f %.12f %.12f %.12f\n', ...
            axis_pos(1), axis_pos(2), axis_pos(3), ...
            axis_dir(1), axis_dir(2), axis_dir(3));
    fclose(fid);
    
    fprintf('✅ Axis saved in SFS format: %s\n', axis_file);
    fprintf('   Position: [%.6f, %.6f, %.6f]\n', axis_pos(1), axis_pos(2), axis_pos(3));
    fprintf('   Direction: [%.6f, %.6f, %.6f]\n', axis_dir(1), axis_dir(2), axis_dir(3));
end

end

