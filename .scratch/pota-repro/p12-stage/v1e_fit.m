% POTA-12 V1e: refinement-objective map on pieces 01-04 (05-08 sealed).
% Selection fixed: raw-GM vote top-1. Per piece: orientation call diagnostic
% (fwd vs rev GM cost per surface at the vote winner), then fixed-orientation
% wide-Huber raw refines at W = 1 (paper control), 5, 10, 25.
function v1e_fit()
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
  Cs = {C0, C1}; rev = [false, false]; om = zeros(2,2);
  for q = 1:2
    Rf = compute_cao_error(top, Cs{q}, false); Rr = compute_cao_error(top, Cs{q}, true);
    cf = sum(apply_robustifier(@robustifier_gm, sum(Rf.^2,1)));
    cr = sum(apply_robustifier(@robustifier_gm, sum(Rr.^2,1)));
    om(q,:) = [cf, cr];
    rev(q) = cr < cf;
  end
  fprintf('V1e P%02d raw-top1 (%.2f,%.2f) %s | orient S0 f=%.3g r=%.3g->%s S1 f=%.3g r=%.3g->%s\n', ...
    frag, da(1), ra(1), passstr(all(pa)), om(1,1), om(1,2), revstr(rev(1)), om(2,1), om(2,2), revstr(rev(2)));
  for W = [1 5 10 25]
    v = af_refine_raw(top, C0, C1, rev, W, 300, 1e-9);
    [dd, rr, pp] = score_vs_shipped(v, SHIP);
    fprintf('  W=%-3d (%.2f,%.2f) %s\n', W, dd(1), rr(1), passstr(all(pp)));
  end
end
end

function s = revstr(b)
if b, s = 'REV'; else, s = 'fwd'; end
end

function s = passstr(ok)
if ok, s = 'PASS'; else, s = 'FAIL'; end
end
