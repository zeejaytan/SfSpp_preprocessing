% Test script to diagnose cross product dimension mismatch
% Based on the error in euc2plucker.m line 16

fprintf('Testing cross product dimension issue...\n');

% Read actual surface data that causes the error
try
    root_dir = '/data/gpfs/projects/punim2657/sfs_preprocessing';
    pot_id = 'A';
    frag_id = 1;
    
    % Read surface files exactly as in read_surfaces.m
    C0_file = sprintf('%s/Surfaces/Plt_%s_Piece_%02d_Surface_0.xyz', root_dir, pot_id, frag_id);
    C1_file = sprintf('%s/Surfaces/Plt_%s_Piece_%02d_Surface_1.xyz', root_dir, pot_id, frag_id);
    
    fprintf('Reading C0 from: %s\n', C0_file);
    fprintf('Reading C1 from: %s\n', C1_file);
    
    % Check if files exist
    if ~exist(C0_file, 'file')
        fprintf('ERROR: C0 file does not exist\n');
        return;
    end
    if ~exist(C1_file, 'file')
        fprintf('ERROR: C1 file does not exist\n');
        return;
    end
    
    % Read files
    C0 = readmatrix(C0_file, 'FileType', 'text');
    C1 = readmatrix(C1_file, 'FileType', 'text');
    
    fprintf('C0 original size: %d x %d\n', size(C0, 1), size(C0, 2));
    fprintf('C1 original size: %d x %d\n', size(C1, 1), size(C1, 2));
    
    % Transpose as done in read_surfaces.m
    C0 = C0';
    C1 = C1';
    
    fprintf('C0 transposed size: %d x %d\n', size(C0, 1), size(C0, 2));
    fprintf('C1 transposed size: %d x %d\n', size(C1, 1), size(C1, 2));
    
    % Match sizes as done in read_surfaces.m
    min_points = min(size(C0, 2), size(C1, 2));
    C0 = C0(:, 1:min_points);
    C1 = C1(:, 1:min_points);
    
    fprintf('After size matching - min_points: %d\n', min_points);
    fprintf('C0 final size: %d x %d\n', size(C0, 1), size(C0, 2));
    fprintf('C1 final size: %d x %d\n', size(C1, 1), size(C1, 2));
    
    % Create line_euc as done in the axis extraction
    line_euc = [C0(1:3,:); C1(1:3,:)];
    fprintf('line_euc size: %d x %d\n', size(line_euc, 1), size(line_euc, 2));
    
    % Extract the parts used in cross product
    part1 = line_euc(4:6,:);  % C1 points
    part2 = line_euc(1:3,:);  % C0 points
    
    fprintf('part1 (line_euc(4:6,:)) size: %d x %d\n', size(part1, 1), size(part1, 2));
    fprintf('part2 (line_euc(1:3,:)) size: %d x %d\n', size(part2, 1), size(part2, 2));
    
    % Test the cross product that fails
    fprintf('Attempting cross product...\n');
    try
        cross_result = cross(part1, part2);
        fprintf('Cross product successful! Result size: %d x %d\n', size(cross_result, 1), size(cross_result, 2));
    catch ME
        fprintf('Cross product failed with error: %s\n', ME.message);
        fprintf('Error identifier: %s\n', ME.identifier);
        
        % Check dimensions more carefully
        fprintf('Detailed dimension analysis:\n');
        fprintf('part1 dimensions: [%s]\n', num2str(size(part1)));
        fprintf('part2 dimensions: [%s]\n', num2str(size(part2)));
        
        % Check if data is valid
        fprintf('part1 contains NaN: %d\n', sum(isnan(part1(:))));
        fprintf('part2 contains NaN: %d\n', sum(isnan(part2(:))));
        fprintf('part1 contains Inf: %d\n', sum(isinf(part1(:))));
        fprintf('part2 contains Inf: %d\n', sum(isinf(part2(:))));
    end
    
catch ME
    fprintf('Script failed with error: %s\n', ME.message);
    fprintf('Error identifier: %s\n', ME.identifier);
end