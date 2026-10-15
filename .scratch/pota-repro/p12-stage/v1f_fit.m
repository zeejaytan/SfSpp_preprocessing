% POTA-12 V1f: close out weighting on pieces 01-04 (05-08 sealed).
% (a) W sweep {0.5,1,2} fixed-orient refine from raw-top1.
% (b) Bias-vs-convergence diagnostic: frozen W=1 cost at shipped vs at
% refined; refine-from-shipped walk (answer used ONLY as a landscape probe,
% never as finder input — same standing as 09's cost diagnostic).
function v1f_fit()
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
  ds = SHIP(1,4:6)'; ds = ds/norm(ds); ps = SHIP(1,1:3)'; ps = ps - ds*(ds'*ps);
  vtship = [ds; ps];
  [VTR, ~, ~] = af_vote(C0, C1, 1000, w, 0, 'raw');
  top = VTR(:,1);
  Cs = {C0, C1}; rev = [false, false];
  for q = 1:2
    Rf = compute_cao_error(top, Cs{q}, false); Rr = compute_cao_error(top, Cs{q}, true);
    cf = sum(apply_robustifier(@robustifier_gm, sum(Rf.^2,1)));
    cr = sum(apply_robustifier(@robustifier_gm, sum(Rr.^2,1)));
    rev(q) = cr < cf;
  end
  [da, ra, pa] = score_vs_shipped(top, SHIP);
  fprintf('V1f P%02d raw-top1 (%.2f,%.2f) %s\n', frag, da(1), ra(1), passstr(all(pa)));
  for W = [0.5 1 2]
    v = af_refine_raw(top, C0, C1, rev, W, 300, 1e-9);
    [dd, rr, pp] = score_vs_shipped(v, SHIP);
    fprintf('  W=%.1f (%.2f,%.2f) %s\n', W, dd(1), rr(1), passstr(all(pp)));
  end
  % diagnostic under frozen W=1 objective with vote-winner orientation
  [F0, F1] = af_freeze_weights(top, C0, C1);
  [~, c_ship] = af_residf(vtship, C0, C1, 0.1, F0, F1);
  v1 = af_refine_raw(top, C0, C1, rev, 1, 300, 1e-9);
  [~, c_v1] = af_residf(v1, C0, C1, 0.1, F0, F1);
  vs = af_refine_raw(vtship, C0, C1, rev, 1, 300, 1e-9);
  [dds, rrs, pps] = score_vs_shipped(vs, SHIP);
  [~, c_vs] = af_residf(vs, C0, C1, 0.1, F0, F1);
  fprintf('  DIAG frozW1: cost(ship)=%.6f cost(ref-from-vote)=%.6f | ref-from-ship (%.2f,%.2f) %s cost=%.6f\n', ...
    c_ship, c_v1, dds(1), rrs(1), passstr(all(pps)), c_vs);
end
end

function s = passstr(ok)
if ok, s = 'PASS'; else, s = 'FAIL'; end
end
