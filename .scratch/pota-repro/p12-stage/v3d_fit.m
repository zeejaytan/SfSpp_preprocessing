% POTA-12 V3d: IRLS threshold sweep on the two floored pieces (fit data only).
% P01/P04 hard-IRLS x8 at thr in {0.5, 1.0, 2.0}: does any threshold break
% the 2.5-3mm floor? (P02 passed at thr=1.0 x8: 5.17 -> 1.86.)
function v3d_fit()
PRIST='/data/gpfs/projects/punim2657/Temp/potsac-p09-pristine/AxisExtraction';
R2FIX='/data/gpfs/projects/punim2657/Temp/potsac-p09-run/r2fix';
SHIM ='/data/gpfs/projects/punim2657/Temp/potsac-p09-run/shim';
P09R ='/data/gpfs/projects/punim2657/Temp/potsac-p09-run';
AFD  ='/data/gpfs/projects/punim2657/Temp/potsac-p12-run/axle_finder';
AXD  ='/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp/Axes';
addpath(SHIM, R2FIX, PRIST, P09R, AFD);
for frag = [1 4]
  [C0, C1] = read_surfaces('A', frag);
  SHIP = readmatrix(sprintf('%s/Pot_A_Piece_%02d_Axis.xyz', AXD, frag), 'FileType','text');
  [VT, ~] = af_vote(C0, C1, 6000, 0.1, 0, 'raw', 6);
  top = VT(:,1);
  Cs = {C0, C1}; rev = [false, false];
  for q = 1:2
    Rf = compute_cao_error(top, Cs{q}, false);
    Rr = compute_cao_error(top, Cs{q}, true);
    cf = sum(apply_robustifier(@robustifier_gm, sum(Rf.^2,1)));
    cr = sum(apply_robustifier(@robustifier_gm, sum(Rr.^2,1)));
    rev(q) = cr < cf;
  end
  v0 = af_refine_raw(top, C0, C1, rev, 1, 300, 1e-9);
  for thr = [0.5 1.0 2.0]
    v = v0;
    for it = 1:8
      [m0, m1, n] = af_inliers(v, C0, C1, rev, thr);
      v = af_refine_raw(v, C0(:,m0), C1(:,m1), rev, 1, 300, 1e-9);
    end
    [dd, rr, pp] = score_vs_shipped(v, SHIP);
    [~, ~, n] = af_inliers(v, C0, C1, rev, thr);
    fprintf('V3d P%02d thr=%.1f it8 n=%d (%.2f,%.2f) %s\n', frag, thr, n, dd(1), rr(1), passstr(all(pp)));
  end
end
end

function s = passstr(ok)
if ok, s = 'PASS'; else, s = 'FAIL'; end
end
