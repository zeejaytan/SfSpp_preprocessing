% Extract NURBS axis results for all Pot A pieces and compare with sample data
fprintf('=== COMPLETE NURBS AXIS EXTRACTION FOR POT A ===\n');

% Extract axes for pieces 3-8
pieces = [3, 4, 5, 6, 7, 8];

fprintf('Extracting NURBS axes for pieces 3-8...\n');
for i = 1:length(pieces)
    piece = pieces(i);
    fprintf('\n--- Processing Piece %02d ---\n', piece);
    
    try
        [vt] = extract_axis_nurbs('A', piece);
        
        if ~isempty(vt)
            % Take the best axis result (first one)
            direction = vt(1:3, 1);
            position = vt(4:6, 1);
            fprintf('✅ Direction: [%.3f, %.3f, %.3f]\n', direction(1), direction(2), direction(3));
            fprintf('✅ Position: [%.3f, %.3f, %.3f]\n', position(1), position(2), position(3));
            
            % Save in sample format
            axis_file = sprintf('Pot_A_Piece_%02d_NURBS_Axis.xyz', piece);
            fid = fopen(axis_file, 'w');
            fprintf(fid, '%.12f %.12f %.12f %.12f %.12f %.12f\n', position(1), position(2), position(3), direction(1), direction(2), direction(3));
            fclose(fid);
            fprintf('💾 Saved to: %s\n', axis_file);
        else
            fprintf('❌ No axis found for piece %02d\n', piece);
        end
        
    catch ME
        fprintf('❌ Error processing piece %02d: %s\n', piece, ME.message);
    end
end

fprintf('\n=== COMPLETE COMPARISON WITH SAMPLE DATA ===\n');

% Compare all pieces (1-8)
all_pieces = [1, 2, 3, 4, 5, 6, 7, 8];

fprintf('\n| Piece | NURBS Position          | Sample Position         | Pos Diff | NURBS Direction      | Sample Direction     | Dir Diff |\n');
fprintf('|-------|-------------------------|-------------------------|----------|----------------------|----------------------|----------|\n');

for i = 1:length(all_pieces)
    piece = all_pieces(i);
    
    % Load sample data
    sample_file = sprintf('/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp/Axes/Pot_A_Piece_%02d_Axis.xyz', piece);
    nurbs_file = sprintf('Pot_A_Piece_%02d_NURBS_Axis.xyz', piece);
    
    if exist(sample_file, 'file') && exist(nurbs_file, 'file')
        sample_data = load(sample_file);
        nurbs_data = load(nurbs_file);
        
        % Calculate differences
        pos_diff = norm(nurbs_data(1:3) - sample_data(1:3));
        dir_diff = norm(nurbs_data(4:6) - sample_data(4:6));
        
        fprintf('| %02d    | [%.1f, %.1f, %.1f] | [%.1f, %.1f, %.1f] | %6.1f   | [%.3f, %.3f, %.3f] | [%.3f, %.3f, %.3f] | %6.3f   |\n', ...
            piece, ...
            nurbs_data(1), nurbs_data(2), nurbs_data(3), ...
            sample_data(1), sample_data(2), sample_data(3), ...
            pos_diff, ...
            nurbs_data(4), nurbs_data(5), nurbs_data(6), ...
            sample_data(4), sample_data(5), sample_data(6), ...
            dir_diff);
    elseif exist(sample_file, 'file')
        sample_data = load(sample_file);
        fprintf('| %02d    | ❌ NURBS Missing        | [%.1f, %.1f, %.1f] | ❌       | ❌ NURBS Missing     | [%.3f, %.3f, %.3f] | ❌       |\n', ...
            piece, ...
            sample_data(1), sample_data(2), sample_data(3), ...
            sample_data(4), sample_data(5), sample_data(6));
    else
        fprintf('| %02d    | ❌ Both Missing         | ❌ Both Missing         | ❌       | ❌ Both Missing      | ❌ Both Missing      | ❌       |\n', piece);
    end
end

fprintf('\n=== SUMMARY STATISTICS ===\n');

% Calculate summary statistics
pos_diffs = [];
dir_diffs = [];

for i = 1:length(all_pieces)
    piece = all_pieces(i);
    sample_file = sprintf('/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp/Axes/Pot_A_Piece_%02d_Axis.xyz', piece);
    nurbs_file = sprintf('Pot_A_Piece_%02d_NURBS_Axis.xyz', piece);
    
    if exist(sample_file, 'file') && exist(nurbs_file, 'file')
        sample_data = load(sample_file);
        nurbs_data = load(nurbs_file);
        
        pos_diffs = [pos_diffs, norm(nurbs_data(1:3) - sample_data(1:3))];
        dir_diffs = [dir_diffs, norm(nurbs_data(4:6) - sample_data(4:6))];
    end
end

if ~isempty(pos_diffs)
    fprintf('Position Differences:\n');
    fprintf('  Mean: %.2f units\n', mean(pos_diffs));
    fprintf('  Std:  %.2f units\n', std(pos_diffs));
    fprintf('  Min:  %.2f units\n', min(pos_diffs));
    fprintf('  Max:  %.2f units\n', max(pos_diffs));
    
    fprintf('Direction Differences:\n');
    fprintf('  Mean: %.3f units\n', mean(dir_diffs));
    fprintf('  Std:  %.3f units\n', std(dir_diffs));
    fprintf('  Min:  %.3f units\n', min(dir_diffs));
    fprintf('  Max:  %.3f units\n', max(dir_diffs));
    
    % Quality assessment
    good_pos = sum(pos_diffs < 5);
    good_dir = sum(dir_diffs < 0.1);
    
    fprintf('\nQuality Assessment:\n');
    fprintf('  Pieces with position error < 5 units: %d/%d (%.0f%%)\n', good_pos, length(pos_diffs), 100*good_pos/length(pos_diffs));
    fprintf('  Pieces with direction error < 0.1 units: %d/%d (%.0f%%)\n', good_dir, length(dir_diffs), 100*good_dir/length(dir_diffs));
end