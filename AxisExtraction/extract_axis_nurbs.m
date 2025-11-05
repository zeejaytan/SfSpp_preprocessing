function vt = extract_axis_nurbs(pot_id, frag_id, extended)
% Extract axis from NURBS-generated surfaces using PotSAC algorithm
% This version is compatible with NURBS preprocessing output

if nargin < 3, extended = false; end

fprintf('=== NURBS AXIS EXTRACTION ===\n');
fprintf('Pot: %s, Fragment: %02d\n', pot_id, frag_id);

% Use NURBS-compatible surface reader
[C0, C1] = read_surfaces_nurbs(pot_id, frag_id, extended);

fprintf('Loaded NURBS surfaces:\n');
fprintf('  Surface 0: %d points\n', size(C0, 2));
fprintf('  Surface 1: %d points\n', size(C1, 2));

% Run PotSAC on NURBS surfaces
% Note: Using every point (no subsampling) for NURBS precision
fprintf('Running PotSAC on NURBS data...\n');
vt = run_potsac(C0(:, 1:1:end), C1(:, 1:1:end));

fprintf('PotSAC completed, extracted %d axis candidates\n', size(vt, 2));

end