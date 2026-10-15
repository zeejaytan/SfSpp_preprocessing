% POTA-12 V1c: raw-select + angular-refine on pieces 01-04 (05-08 sealed).
% Selection stays 100% raw GM (global shape); angular cost used ONLY inside
% af_refine (local sharpness). Compares against V1b (angular re-rank broke P03).
function v1c_fit()
PRIST='/data/gpfs/projects/punim2657/Temp/potsac-p09-pristine/AxisExtraction';
R2FIX='/data/gpfs/projects/punim2657/Temp/potsac-p09-run/r2fix';
SHIM ='/data/gpfs/projects/punim2657/Temp/potsac-p09-run/shim';
P09R ='/data/gpfs/projects/punim2657/Temp/potsac-p09-run';
AFD  ='/data/gpfs/projects/punim2657/Temp/potsac-p12-run/axle_finder';
AXD  ='/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp/Axes';
addpath(SHIM, R2FIX, PRIST, P09R, AFD);
w = 0.1;
for frag = 1:4
  [C0, C1] = read_surfaces('A', frag);
  SHIP = readmatrix(sprintf('%s/Pot_A_Piece_%02d_Axis.xyz', AXD, frag), 'FileType','text');
  [VTR, ~, ~] = af_vote(C0, C1, 1000, w, 0, 'raw');
  top = VTR(:,1);
  [da, ra, pa] = score_vs_shipped(top, SHIP);
  v1 = af_refine(top, C0(:,1:10:end), C1(:,1:10:end), w, 300, 1e-3);
  [d1, r1, p1] = score_vs_shipped(v1, SHIP);
  v2 = af_refine(v1, C0, C1, w, 300, 1e-9);
  [d2, r2, p2] = score_vs_shipped(v2, SHIP);
  fprintf('V1c P%02d raw-top1 (%.2f,%.2f) %s | sub (%.2f,%.2f) %s | full (%.2f,%.2f) %s\n', ...
    frag, da(1), ra(1), passstr(all(pa)), d1(1), r1(1), passstr(all(p1)), d2(1), r2(1), passstr(all(p2)));
end
end

function s = passstr(ok)
if ok, s = 'PASS'; else, s = 'FAIL'; end
end
