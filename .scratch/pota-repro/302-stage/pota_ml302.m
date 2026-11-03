% Ticket 302 gate 2, MATLAB arm: run_potsac (adaptive step) on corpus Pot A.
% rng(0) per piece. Writes out_ml/Pot_A_Piece_NN_Axis.xyz (position-first rows).
C0ROOT = '/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp/Surfaces';
outdir = getenv('OUTDIR');
cd_ = getenv('AXDIR');   % AxisExtraction with run_potsac.m
addpath(cd_);
for piece = 1:8
    stem = sprintf('Pot_A_Piece_%02d', piece);
    S0 = load(fullfile(C0ROOT, [stem '_Surface_0.xyz']));
    S1 = load(fullfile(C0ROOT, [stem '_Surface_1.xyz']));
    C0 = S0'; C1 = S1';
    rng(0);
    vt = run_potsac(C0, C1);
    K = size(vt, 2);
    rows = [vt(4:6, :)', vt(1:3, :)'];   % position-first
    writematrix(rows, fullfile(outdir, [stem '_Axis.xyz']), 'FileType', 'text', 'Delimiter', ' ');
    nl = sprintf('\n');
    fprintf(strjoin({'%s K=%d dir=[%.6f %.6f %.6f] pos=[%.6f %.6f %.6f]', ''}, nl), stem, K, ...
        vt(1,1), vt(2,1), vt(3,1), vt(4,1), vt(5,1), vt(6,1));
end
disp('MATLAB arm done');
