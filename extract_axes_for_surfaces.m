function extract_axes_for_surfaces()
% Dynamically extract axes for all available surfaces in a directory.
% Reads SURFACES_DIR from env; defaults to 'Dataset/SfS_pp/Surfaces'.
% Writes results to NURBS_Output/Axes with basename-derived filenames.

fprintf('=== Dynamic NURBS Axis Extraction ===\n');
addpath('original_nurbs_preprocessing/AxisExtraction');
addpath('AxisExtraction');

surfaces_dir = getenv('SURFACES_DIR');
if isempty(surfaces_dir)
    surfaces_dir = 'Dataset/SfS_pp/Surfaces';
end
fprintf('Surface dir: %s\n', surfaces_dir);

files = builtin('dir', fullfile(surfaces_dir, '*_Surface_0.xyz'));
if isempty(files)
    fprintf('No surface files found at %s\n', surfaces_dir);
    return;
end

% Prepare output dirs
out_dir = 'NURBS_Output/Axes';
if ~exist('NURBS_Output', 'dir'); mkdir('NURBS_Output'); end
if ~exist(out_dir, 'dir'); mkdir(out_dir); end

success = 0;
for k = 1:numel(files)
    f0 = fullfile(surfaces_dir, files(k).name);
    base = regexprep(files(k).name, '_Surface_0\.xyz$', '');
    f1 = fullfile(surfaces_dir, [base '_Surface_1.xyz']);
    if ~exist(f1, 'file')
        fprintf('  Skipping %s (missing Surface_1)\n', base);
        continue;
    end
    fprintf('\n--- Processing %s ---\n', base);

    try
        % Load surfaces (X Y Z Nx Ny Nz)
        S0 = readmatrix(f0, 'FileType', 'text');
        S1 = readmatrix(f1, 'FileType', 'text');
        % Build [6 x N] combined data (points; normals)
        pts = [S0(:,1:3); S1(:,1:3)];
        nrm = [S0(:,4:6); S1(:,4:6)];
        C = [pts nrm]';

        vt = run_potsac(C);
        if size(vt,1) < 6 || size(vt,2) < 1
            fprintf('  No valid axis candidates returned\n');
            continue;
        end

        axis_file = fullfile(out_dir, [base '_Axis.xyz']);
        fid = fopen(axis_file, 'w');
        for c = 1:size(vt,2)
            r13 = vt(1:3,c); r46 = vt(4:6,c);
            n13 = norm(r13); n46 = norm(r46);
            if abs(n13-1.0) < 0.1
                dir = r13 / max(n13, eps);
                pos = r46;
            elseif abs(n46-1.0) < 0.1
                dir = r46 / max(n46, eps);
                pos = r13;
            else
                dir = r13 / max(n13, eps);
                pos = r46;
            end
            fprintf(fid, '%.6f %.6f %.6f %.6f %.6f %.6f\n', pos(1), pos(2), pos(3), dir(1), dir(2), dir(3));
        end
        fclose(fid);
        fprintf('  ✅ Saved axis: %s\n', axis_file);
        success = success + 1;
    catch ME
        fprintf('  ❌ Axis extraction failed for %s: %s\n', base, ME.message);
    end
end

fprintf('\n=== Axis Extraction Complete: %d/%d pieces ===\n', success, numel(files));

end
