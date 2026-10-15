% POTA-12 V3: kill the 0.5-3mm position bias on fit data (05-08 sealed).
% (a) hard-IRLS pilot: iterate refine-on-tight-inliers-only (|R|<=1, frozen
%     orient, W=1) x3 from the vote start. Huber-linear tails let outliers
%     keep pulling; hard rejection removes the pull entirely.
% (b) small-patch test: spatial ball crops of P01 at 07-scale (~1.7k pts per
%     surface); full af_find_all on each; score vs shipped.
function v3_fit()
PRIST='/data/gpfs/projects/punim2657/Temp/potsac-p09-pristine/AxisExtraction';
R2FIX='/data/gpfs/projects/punim2657/Temp/potsac-p09-run/r2fix';
SHIM ='/data/gpfs/projects/punim2657/Temp/potsac-p09-run/shim';
P09R ='/data/gpfs/projects/punim2657/Temp/potsac-p09-run';
AFD  ='/data/gpfs/projects/punim2657/Temp/potsac-p12-run/axle_finder';
AXD  ='/data/gpfs/projects/punim2657/sfs_main/original_samples/SfS_pp/Axes';
addpath(SHIM, R2FIX, PRIST, P09R, AFD);
for frag = 1:4
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
  v = af_refine_raw(top, C0, C1, rev, 1, 300, 1e-9);
  [dd, rr, pp] = score_vs_shipped(v, SHIP);
  fprintf('V3a P%02d round0 full (%.2f,%.2f) %s', frag, dd(1), rr(1), passstr(all(pp)));
  R0 = C0; R1 = C1;
  for it = 1:3
    [m0, m1, n] = af_inliers(v, R0, R1, rev, 1.0);
    v = af_refine_raw(v, R0(:,m0), R1(:,m1), rev, 1, 300, 1e-9);
    [dd, rr, pp] = score_vs_shipped(v, SHIP);
    fprintf(' | it%d n=%d (%.2f,%.2f) %s', it, n, dd(1), rr(1), passstr(all(pp)));
  end
  fprintf('\n');
end
% (b) small patches of P01
[Q0, Q1] = read_surfaces('A', 1);
SH = readmatrix([AXD '/Pot_A_Piece_01_Axis.xyz'], 'FileType','text');
X = [Q0(1:3,:), Q1(1:3,:)];
rng(11);
seeds = X(:, randsample(size(X,2), 3));
for s = 1:3
  d = sqrt(sum((X - seeds(:,s)).^2, 1));
  r = 0; for rad = 5:5:200
    if sum(d <= rad) >= 3400, r = rad; break; end
  end
  sel = d <= r;
  n0 = sum(sel(1:size(Q0,2))); n1 = sum(sel) - n0;
  [VOUT, ~] = af_find_all(Q0(:,sel(1:size(Q0,2))), Q1(:,sel(size(Q0,2)+1:end)), s);
  [dd, rr, pp] = score_vs_shipped(VOUT, SH);
  fprintf('V3b patch%d rad=%d n=(%d,%d) nset=%d derr=[%s] rerr=[%s] %s\n', s, r, n0, n1, ...
    size(VOUT,2), num2str(dd','%.2f '), num2str(rr','%.2f '), passstr(all(pp)));
end
end

function s = passstr(ok)
if ok, s = 'PASS'; else, s = 'FAIL'; end
end
