% unit302.m -- ticket 302 stage 1 MATLAB side.
% For every CELLS/<cell>: [R1,J] = compute_biaxial_cao_error(vt, X) and
% [R3,~] = compute_cao_error(vt, X); dump R1 (n), J as 6 columns (row i =
% J(1,:,i)), R3 (n x 3). run_dir passed via -batch environment.
addpath('/data/gpfs/projects/punim2657/sfs_preprocessing/AxisExtraction');
run_dir = getenv('RUN302');
cells_dir = fullfile(run_dir, 'work', 'inputs', 'CELLS');
d = dir(cells_dir); d = d([d.isdir]);
names = {};
for k = 1:numel(d)
    nm = d(k).name;
    if ~startsWith(nm, '.'), names{end+1} = nm; end %#ok<*SAGROW>
end
names = sort(names);
fprintf('cells: %s\n', strjoin(names, ' '));
for k = 1:numel(names)
    cell = names{k};
    cd_ = fullfile(cells_dir, cell);
    X = readmatrix(fullfile(cd_, 'X.tsv'), 'FileType', 'text', 'Delimiter', '\t')';   % 6 x n
    vt = readmatrix(fullfile(cd_, 'vt.tsv'), 'FileType', 'text', 'Delimiter', '\t');
    vt = vt(:);
    [R1, J] = compute_biaxial_cao_error(vt, X);
    R3 = compute_cao_error(vt, X);
    writematrix(R1(:), fullfile(cd_, 'ml_R1.tsv'), 'FileType', 'text', 'Delimiter', '\t');
    writematrix(reshape(J, 6, [])', fullfile(cd_, 'ml_J6.tsv'), 'FileType', 'text', 'Delimiter', '\t');
    writematrix(R3', fullfile(cd_, 'ml_R3.tsv'), 'FileType', 'text', 'Delimiter', '\t');
    fprintf('%s: n=%d  max|R1|=%.6g  max|J|=%.6g\n', cell, size(X,2), max(abs(R1)), max(abs(J(:))));
end
fprintf('MATLAB side done\n');
