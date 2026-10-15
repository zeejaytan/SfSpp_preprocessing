% POTA-12 V1b: staged weighting fit on pieces 01-04 (sealed 05-08 never loaded).
% Stage A (global): vote ranked by raw GM cost -> top 50 (paper chain statistic).
% Stage B (local): re-rank 50 by angular cost -> top 1.
% Stage C: angular sub-refine (10%) + angular full refine.
function v1b_fit()
PRIST='/data/gpfs/projects/punim2657/Temp/potsac-p09-pristine/AxisExtraction';
R2FIX='/data/gpfs/projects/punim2657/Temp/potsac-p09-run/r2fix';
SHIM ='/data/gpfs/projects/punim2657/Temp/potsac-p09-run/shim';
P09R ='/data/gpfs/projects/punim2657/Temp/potsac-p09-run';
AFD  ='/data/gpfs/projects/punim2657/Temp/potsac-p12-run/axle_finder';
AXD  ='/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp/Axes';
addpath(SHIM, R2FIX, PRIST, P09R, AFD);
w = 0.1; K = 50;
for frag = 1:4
  [C0, C1] = read_surfaces('A', frag);
  SHIP = readmatrix(sprintf('%s/Pot_A_Piece_%02d_Axis.xyz', AXD, frag), 'FileType','text');
  [VTR, ~, CA] = af_vote(C0, C1, 1000, w, 0, 'raw');
  [da0, ra0, pa0] = score_vs_shipped(VTR(:,1), SHIP);
  % diagnostic: raw rank of the best-angular candidate far from shipped (>10deg)
  dpop = zeros(1000,1);
  for j = 1:1000
    [dj, ~, ~] = score_vs_shipped(VTR(:,j), SHIP);
    dpop(j) = dj(1);
  end
  far = find(dpop > 10);
  [~, jb] = min(CA(far));
  fprintf('V1b P%02d spur: raw-rank=%d angular=%.6f | A-top1 (%.2f,%.2f) %s\n', ...
    frag, far(jb), CA(far(jb)), da0(1), ra0(1), passstr(all(pa0)));
  CAND = VTR(:,1:K); CAC = CA(1:K);
  [~, ib] = sort(CAC); top = CAND(:,ib(1));
  [da, ra, pa] = score_vs_shipped(top, SHIP);
  v1 = af_refine(top, C0(:,1:10:end), C1(:,1:10:end), w, 300, 1e-3);
  [d1, r1, p1] = score_vs_shipped(v1, SHIP);
  v2 = af_refine(v1, C0, C1, w, 300, 1e-9);
  [d2, r2, p2] = score_vs_shipped(v2, SHIP);
  fprintf('  B-top1 (%.2f,%.2f) %s | sub (%.2f,%.2f) %s | full (%.2f,%.2f) %s\n', ...
    da(1), ra(1), passstr(all(pa)), d1(1), r1(1), passstr(all(p1)), d2(1), r2(1), passstr(all(p2)));
end
end

function s = passstr(ok)
if ok, s = 'PASS'; else, s = 'FAIL'; end
end
