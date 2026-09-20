% run_juglet_axes.m -- Juglet axis extraction (9 sherds, PotSAC).
% Called as: matlab -batch "run_juglet_axes"  (single line: the Nov-2025
% tooling silently runs only the FIRST LINE of a multi-line -batch string --
% bit 30825982: LINE-ONE printed, LINE-TWO skipped, exit 0. A script file
% sidesteps shell quoting entirely.)
POT_ID = 'A';  % legacy label only; naming comes from file paths below
POT_NAME = 'Juglet';
NUM_PIECES = 9;
OUTPUT_BASE = '/data/gpfs/projects/punim2657/sfs_preprocessing/Juglet_Dataset_20260916';

addpath('.');
ok = 0;
for piece = 1:NUM_PIECES
    piece_str = sprintf('%d', piece);
    surface_file = sprintf('%s/SfS_pp/Surfaces/%s_Piece_%s_Surface_0.xyz', OUTPUT_BASE, POT_NAME, piece_str);
    output_file = sprintf('%s/SfS_pp/Axes/%s_Piece_%s_Axis.xyz', OUTPUT_BASE, POT_NAME, piece_str);
    fprintf('Processing piece %s/%d...\n', piece_str, NUM_PIECES);
    if exist(surface_file, 'file')
        try
            extract_single_axis(POT_ID, piece, surface_file, output_file);
            fprintf('ok piece %s\n', piece_str);
            ok = ok + 1;
        catch ME
            fprintf('FAILED piece %s: %s\n', piece_str, ME.message);
        end
    else
        fprintf('missing surface: %s\n', surface_file);
    end
end
fprintf('axis extraction done: %d/%d\n', ok, NUM_PIECES);
if ok ~= NUM_PIECES
    error('juglet_axes:incomplete', 'only %d/%d axes produced', ok, NUM_PIECES);
end
